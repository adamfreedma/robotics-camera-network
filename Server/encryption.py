import random
import socket
import threading
from secrets import randbits
from sympy import isprime


class Encryption(object):

    def __init__(self, connection: socket.socket):

        self.private_key = random.randint(2**25, 2**31)
        self.secret_key = 0

        self.exchange_thread = threading.Thread(target=self.exchange, args=[connection])
        self.exchange_thread.start()

    def exchange(self, connection: socket.socket):
        print("stated exchange")
        p = _choose_p()
        g = -2 % p

        print(p, g)

        message = str(p).zfill(10) + str(g).zfill(10)
        try:
            connection.send(message.encode())
        except socket.error:
            print("connetion terminated, exchange")
        print(message)

        generated_key = (g ** self.private_key) % p
        received_key = ""
        try:
            received_key = connection.recv(10).decode()
            connection.send(str(generated_key).encode())
        except socket.error:
            print("connection terminated, key exchange")
        print(received_key)

        try:
            received_key = int(received_key)
        except TypeError:
            print("invalid input, key exchange")

        self.secret_key = (received_key ** self.private_key) % p
        print(self.secret_key)


def _choose_p():
    while True:
        p = find_pseudoprime(32)  # Find a pseudoprime
        # If (p-1)/2 is also prime, then we've completed
        # step 1 of the Diffie-Hellman Key Exchange.
        # check if 2 has order (p-1)//2 for security reasons.
        if pow(2, (p - 1) // 2, p) == p - 1:
            return p


def find_pseudoprime(bit_count):
    n = bit_count // 2
    while True:
        q = randbits(n)
        if isprime(q) and q % 12 == 1 and isprime(2 * q - 1):
            return q * (2 * q - 1)
