import socket
import select
import threading
from typing import Tuple, List, Dict
import encryption
import database
from scapy.layers.l2 import getmacbyip


class Connection(object):

    MAX_QUEUE_SIZE = 1

    def __init__(self, server_port: int, client_count=3):
        self.server_port = server_port

        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', self.server_port))
        self.server_socket.listen(client_count)
        self.encryptors: Dict[socket.socket, encryption.Encryption] = {}
        self.database = database.Database('robotics.db')

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
                    print("from send waiting")
                    messages_to_send_cleared = [msg for msg in messages if msg[0] is client_socket]
                    messages = messages_to_send_cleared

    @staticmethod
    def _get_mac(ip_address: str) -> str:
        """
        gets the mac address by the ip address
        :param ip_address: ip address to check
        :return: the mac address
        """
        return getmacbyip(ip_address)

    @staticmethod
    def unpack_protocol(msg: str) -> Tuple[float, float]:
        """
        unpacks the protocol from a xxxxx.xxxxx str to a float
        :param msg:
        :return:
        """
        # move decimal spot 5 places
        x = float(msg[:10]) / 100000
        y = float(msg[10:]) / 100000

        return x, y

    def _run(self):
        """
        main loop
        """
        while True:
            r_list, w_list, x_list = select.select([self.server_socket] + list(self.open_client_sockets.keys()),
                                                   [self.server_socket] + list(self.open_client_sockets.keys()), [])
            for curr_socket in r_list:
                # checking for new connections
                if curr_socket is self.server_socket:
                    (new_client, address) = self.server_socket.accept()
                    print(self._get_mac(address[0]))
                    name, location = self.database.camera_info(self._get_mac(address[0]))
                    if name:
                        # sending accept message to the client since it is approved in the database
                        new_client.send("ack".encode())
                        for axis in location:
                            new_client.send(str(axis).zfill(10).encode())
                        print(f'{address[0]}, {name},  connected to the server')
                        self.encryptors[new_client] = encryption.Encryption(new_client)
                        self.open_client_sockets[new_client] = address[0]
                    else:
                        try:
                            new_client.send("rej".encode())
                            new_client.close()
                        except Exception as e:
                            print(str(e))
                            print("from sending rej")
                elif self.encryptors[curr_socket].exchange_done:
                    input_data = ""
                    try:
                        # getting input data
                        encrypted_input_data = curr_socket.recv(64)
                        input_data = self.encryptors[curr_socket].decrypt(encrypted_input_data).zfill(20)
                    except Exception as e:
                        print(str(e))
                        self._handle_disconnected_client(curr_socket)
                        print("from receive message")

                    if input_data == "":
                        self._handle_disconnected_client(curr_socket)
                        print("from empty message")
                    else:
                        self.lock.acquire()
                        self.incoming_messages.append((curr_socket, input_data))
                        while len(self.incoming_messages) > self.MAX_QUEUE_SIZE:
                            self.incoming_messages.pop()
                        self.lock.release()

            self._send_waiting_messages(w_list, self.messages_to_send)
