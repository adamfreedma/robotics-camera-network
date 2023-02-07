import random
import socket
import threading


class Encryption(object):

    def __init__(self, connection: socket.socket):

        self.private_key = random.randint(2**25, 2**31)
        self.secret_key = 0

        self.exchange_thread = threading.Thread(target=self.exchange, args=[connection])
        self.exchange_thread.start()

    def exchange(self, connection: socket.socket):
        print("stated exchange")

        keys = ""
        try:
            keys = connection.recv(20).decode()
            keys.zfill(20)
        except socket.error:
            print("connection terminated, key exchange")

        p = 0
        g = 0

        try:
            p = int(keys[10:])
            g = int(keys[:10])
        except TypeError:
            print("invalid input, key exchange")
        print(g, p, 0)
        print(5)
        generated_key = (g ** self.private_key) % p
        print(6)
        received_key = ""
        print(self.private_key)
        try:
            connection.send(str(generated_key).encode())
            received_key = connection.recv(10).decode()
        except socket.error:
            print("connection terminated, key exchange")

        try:
            received_key = int(received_key)
        except TypeError:
            print("invalid input, key exchange")
        print(received_key)

        self.secret_key = (received_key ** self.private_key) % p
        print(self.secret_key)

