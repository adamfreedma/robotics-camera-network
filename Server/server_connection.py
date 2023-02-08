import socket
import select
import threading
from typing import Tuple, List
import encryption


class Connection(object):

    MAX_QUEUE_SIZE = 1

    def __init__(self, server_port, client_count=3):
        self.server_port = server_port

        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', self.server_port))
        self.server_socket.listen(client_count)

        # clients
        self.open_client_sockets = {}
        self.messages_to_send = []
        self.incoming_messages = []

        # starting the run thread
        self.lock = threading.Lock()

        self.run_thread = threading.Thread(target=self._run, daemon=True)
        self.run_thread.start()

    def _disconnect_all_clients(self):
        """disconnects all connected client sockets
        """
        for client_socket in self.open_client_sockets:
            client_socket.close()
        self.open_client_sockets = {}

    def _handle_disconnected_client(self, client_socket: socket.socket):
        """disconnects a single socket and removes it from lists he is in

        Args:
            client_socket (socket): socket to disconnect
        """
        try:
            if client_socket in self.open_client_sockets:
                print(f'{self.open_client_sockets[client_socket]} - disconnected')
                del self.open_client_sockets[client_socket]
                client_socket.close()
        except Exception as e:
            print(e)

    def _send_waiting_messages(self, wlist, messages: List[Tuple[socket.socket, str]]):
        """sends all messages that are currently in the message queue

        Args:
            wlist (list of sockets): sockets that are ready to write to
            messages (list of (socket, str)): messages to send
        """
        for message in messages:
            client_socket, msg = message
            if client_socket in wlist:
                try:
                    client_socket.send(msg.encode())
                    messages.remove(message)
                except socket.error:
                    self._handle_disconnected_client(client_socket)
                    messages_to_send_cleared = [msg for msg in messages if msg[0] is client_socket]
                    messages = messages_to_send_cleared

    def _run(self) -> None:
        """main loop
        """
        while True:
            r_list, w_list, x_list = select.select([self.server_socket] + list(self.open_client_sockets.keys()),
                                                   [self.server_socket] + list(self.open_client_sockets.keys()), [])
            for curr_socket in r_list:
                # checking for new connections
                if curr_socket is self.server_socket:
                    (new_client, address) = self.server_socket.accept()
                    print(f'{address[0]}, connected to the server')
                    self.open_client_sockets[new_client] = address[0]
                    # TODO - change to mac address check
                    self.encryptor = encryption.Encryption(new_client)

                else:
                    input_data = ""
                    try:
                        # getting input data
                        encrypted_input_data = curr_socket.recv(64)
                        input_data = self.encryptor.decrypt(encrypted_input_data)
                    except Exception as e:
                        print(str(e))
                        self._handle_disconnected_client(curr_socket)

                    if input_data == "":
                        self._handle_disconnected_client(curr_socket)
                    else:
                        self.lock.acquire()
                        self.incoming_messages.append((curr_socket, input_data))
                        while len(self.incoming_messages) > self.MAX_QUEUE_SIZE:
                            self.incoming_messages.pop()
                        self.lock.release()

            self._send_waiting_messages(w_list, self.messages_to_send)
