import socket
import threading
from typing import Union, List
import encryption
import time

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
        self.encryptor = encryption.Encryption(self.server_socket)
        self.finished_exchange = False
        self.accepted = False
        self.wait_for_ack_thread = threading.Thread(target=self._wait_for_ack, daemon=True)
        self.wait_for_ack_thread.start()

    def _wait_for_ack(self):
        """
        waiting for the servers response
        :return: putting response into self.accepted
        """
        while not self.encryptor.finished_exchange:
            time.sleep(0.1)
        answer = ""
        try:
            answer = self.server_socket.recv(3).decode()
        except socket.error:
            print("Connection interrupted whilst waiting for ack")

        if answer == "ack":
            self.accepted = True
            print("accepted by the server")
        else:
            print("rejected by the server")
            self.accepted = False

    def _str_protocol(self, data: Union[any, List[any]]) -> str:
        """
        :param data: data to send
        :return: the data according to the protocol
        """
        msg = ""
        # making the str a list
        if type(data) != list:
            data = [data]
        # making a fixed length to each part of the message
        part_length = self.MSG_LENGTH // len(data)

        for part in data:
            msg += str(part).zfill(part_length)

        msg.zfill(self.MSG_LENGTH)
        return msg

    def send(self, data: Union[str, List[str]]):
        """
        :param data: str or List[str]
        :return: sends the data to the server
        """
        # only sending if we are accepted
        if self.accepted:
            msg = self._str_protocol(data)
            encrypted_msg = self.encryptor.encrypt(msg)

            try:
                self.server_socket.send(encrypted_msg)
            except socket.error as e:
                exit("Connection interrupted, send" + str(e))
