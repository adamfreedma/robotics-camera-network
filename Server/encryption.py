import random
import socket
import threading
from secrets import randbits
from sympy import isprime
from Crypto.Cipher import AES
from Crypto import Random
import base64
import hashlib


class Encryption(object):

    BLOCK_SIZE = 16

    def __init__(self, connection: socket.socket, client_list, address):

        self.private_key = random.randint(2**25, 2**31)
        self.secret_key = bytes()

        self.exchange_thread = threading.Thread(target=self._exchange, args=[connection, client_list, address])
        self.exchange_thread.start()

    def _exchange(self, connection: socket.socket, client_list, address):
        """
        Diffie Hellman key exhange with the client
        :param connection: socket of the client to exchange with
        :return: exchanges secret ket with the client using the Diffie Hellman method
        """

        # generating P and G value for the exchange, where P is a large prime and G is the base
        p = self._choose_p()
        g = -2 % p

        message = str(p).zfill(100) + str(g).zfill(100)
        try:
            connection.send(message.encode())
        except socket.error:
            print("connetion terminated, exchange")
        generated_key = self._mod_power(g, self.private_key, p)
        received_key = ""
        try:
            received_key = connection.recv(100).decode()
            connection.send(str(generated_key).zfill(100).encode())
        except socket.error:
            print("connection terminated, key exchange")

        try:
            received_key = int(received_key)
        except Exception as e:
            print("invalid input, key exchange", e)

        secret_key_number = self._mod_power(received_key, self.private_key, p)
        self.secret_key = hashlib.sha256(str(secret_key_number).encode()).digest()
        client_list[connection] = address[0]

    def encrypt(self, string: str) -> bytes:
        """
        encrypts a string
        :param string: string to encrypt
        :return: the encrypted string
        """
        string = self._pad(string)
        starting_vector = Random.new().read(self.BLOCK_SIZE)
        cipher = AES.new(self.secret_key, AES.MODE_CBC, starting_vector)
        return base64.b64encode(starting_vector + cipher.encrypt(string.encode()))

    def decrypt(self, encrypted_string: bytes) -> str:
        """
        decrypts an encrypted string
        :param encrypted_string: the encrypted string
        :return: the decrypted stirng
        """
        encrypted_string = base64.b64decode(encrypted_string)
        starting_vector = encrypted_string[:self.BLOCK_SIZE]
        cipher = AES.new(self.secret_key, AES.MODE_CBC, starting_vector)
        return self._unpad(cipher.decrypt(encrypted_string[self.BLOCK_SIZE:])).decode()

    def _pad(self, string: str) -> str:
        """
        pads the string if it isn't a multiple of block size for encryption
        :param self:
        :param string: string to pad
        :return: the string padded
        """
        return string + (self.BLOCK_SIZE - len(string) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(string)
                                                                                % self.BLOCK_SIZE)

    @staticmethod
    def hash(string: str):
        return hashlib.sha256(string.encode()).hexdigest()


    @staticmethod
    def _unpad(string: bytes) -> bytes:
        """
        unpads the string after encryption+decryption
        :param string: the string to unpad
        :return: the unpadded string
        """
        return string[:-ord(string[len(string) - 1:])]

    @staticmethod
    def _choose_p() -> int:
        """
        chooses a random large prime number
        :return: a large prime number
        """
        while True:
            p = Encryption._find_pseudoprime(128)  # Find a pseudoprime
            # If (p-1)/2 is also prime, then we've completed
            # step 1 of the Diffie-Hellman Key Exchange.
            # check if 2 has order (p-1)//2 for security reasons.
            if pow(2, (p - 1) // 2, p) == p - 1:
                return p

    @staticmethod
    def _find_pseudoprime(bit_count: int) -> int:
        """
        generates random numbers until it finds a pseudoprime
        :param bit_count: number of bits in numbers to search
        :return: the found pseudoprime
        """
        n = bit_count // 2
        while True:
            q = randbits(n)
            if isprime(q) and q % 12 == 1 and isprime(2 * q - 1):
                return q * (2 * q - 1)

    @staticmethod
    def _mod_power(base: int, power: int, modulo: int) -> int:
        """
        calculates modulo power in O(log(n)) time complexity where n=power
        :param base: the base of the power
        :param power: the exponent of the poewr
        :param modulo: the modulo to use
        :return: the result of the exponent
        """
        if power == 0:
            return 1
        n = Encryption._mod_power(base, power // 2, modulo) % modulo
        if power % 2 == 0:
            return n * n % modulo
        else:
            if power > 0:
                return base * n * n % modulo
            else:
                return ((n * n) // base) % modulo
