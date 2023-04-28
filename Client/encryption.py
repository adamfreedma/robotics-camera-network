import random
import socket
import threading
from Crypto.Cipher import AES
from Crypto import Random
import base64
import hashlib


class Encryption(object):

    BLOCK_SIZE = 16

    def __init__(self, connection: socket.socket):

        self.private_key = random.randint(2**25, 2**31)
        self.secret_key = bytes()

        self.exchange_thread = threading.Thread(target=self.exchange, args=[connection], daemon=True)
        self.exchange_thread.start()
        self.finished_exchange = False

    def exchange(self, connection: socket.socket):

        keys = ""
        try:
            keys = connection.recv(200).decode()
            keys.zfill(200)
        except socket.error:
            print("connection terminated, key exchange")

        p = 0
        g = 0

        try:
            g = int(keys[100:])
            p = int(keys[:100])
        except TypeError:
            print("invalid input, key exchange")
        generated_key = self._mod_power(g, self.private_key, p)
        received_key = ""
        try:
            connection.send(str(generated_key).zfill(100).encode())
            received_key = connection.recv(100).decode()
        except socket.error:
            print("connection terminated, key exchange")

        try:
            received_key = int(received_key)
        except ValueError:
            print("invalid input, key exchange")

        secret_key_number = self._mod_power(received_key, self.private_key, p)
        self.secret_key = hashlib.sha256(str(secret_key_number).encode()).digest()
        self.finished_exchange = True

    def encrypt(self, string):
        string = self._pad(string)
        starting_vector = Random.new().read(self.BLOCK_SIZE)
        cipher = AES.new(self.secret_key, AES.MODE_CBC, starting_vector)
        return base64.b64encode(starting_vector + cipher.encrypt(string.encode()))

    def decrypt(self, encrypted_string):
        encrypted_string = base64.b64decode(encrypted_string)
        starting_vector = encrypted_string[:self.BLOCK_SIZE]
        cipher = AES.new(self.secret_key, AES.MODE_CBC, starting_vector)
        return self._unpad(cipher.decrypt(encrypted_string[self.BLOCK_SIZE:])).decode()

    def _pad(self, string):
        """
        pads the string if it isn't a multiple of block size for encryption
        :param self:
        :param string: string to pad
        :return: the string padded
        """
        return string + (self.BLOCK_SIZE - len(string) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(string)
                                                                                % self.BLOCK_SIZE)

    @staticmethod
    def _unpad(string):
        return string[:-ord(string[len(string) - 1:])]

    @staticmethod
    def _mod_power(base, power, modulo):
        if power == 0:
            return 1
        n = Encryption._mod_power(base, power // 2, modulo) % modulo
        if power % 2 == 0:
            return n * n % modulo
        else:
            if power > 0:
                return base * n * n % modulo
            else:
                return ((n * n) / base) % modulo
