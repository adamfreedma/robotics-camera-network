import socket
import threading
from typing import Union, List


class Connection(object):

    # the message length the server expects
    MSG_LENGTH = 20

    def __init__(self, server_ip: str, server_port: int):
        self.server_ip = server_ip
        self.server_port = server_port

        self._connect()

    def _connect(self):
        """
        connects to the server and waits for the response
        :return:
        """
        self.server_socket = socket.socket()
        self.server_socket.connect((self.server_ip, self.server_port))
        # checking if the server approves us
        self.accepted = False
        self.wait_for_ack_thread = threading.Thread(target=self._wait_for_ack)
        self.wait_for_ack_thread.start()

    def _wait_for_ack(self):
        """
        waiting for the servers response
        :return: putting response into self.accepted
        """
        answer = ""
        try:
            answer = self.server_socket.recv(3).decode()
        except socket.error:
            print("Connection interrupted whilst waiting for ack")

        if answer == "ack":
            self.accepted = True
        else:
            print("rejected by the server")
            self.accepted = False

    def send(self, data: Union[str, List[str]]):
        """
        :param data: str or List[str]
        :return: sends the data to the server
        """
        # only sending if we are accepted
        if self.accepted:
            msg = ""
            # making the str a list
            if type(data) == str:
                data = tuple(data)
            # making a fixed length to each part of the message
            part_length = self.MSG_LENGTH // len(data)

            for part in data:
                msg += part.zfill(part_length)

            msg.zfill(self.MSG_LENGTH)
