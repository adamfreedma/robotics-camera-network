import server_connection
import time
import merger


def main():
    connection = server_connection.Connection(3333)
    object_merger = merger.Merger()
    start = time.time()
    while True:

        connection.lock.acquire()
        for msg in connection.incoming_messages:
            object_merger.insert_client_object(float(msg[1][:10]), float(msg[1][10:]))

        connection.incoming_messages = []
        connection.lock.release()


if __name__ == '__main__':
    main()