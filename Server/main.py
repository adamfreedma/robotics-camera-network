import server_connection
import time
import merger
import gui
import detector

gui_object = gui.GUI()
gui_object.start()

def main():
    connection = server_connection.Connection(3333)
    object_merger = merger.Merger()
    start = time.time()
    while True:
        connection.lock.acquire()
        for msg in connection.incoming_messages:
            x, y = connection.unpack_protocol(msg[1])
            object_merger.insert_client_object(x, y)
        connection.incoming_messages = []
        connection.lock.release()
        gui_object.draw_cones(object_merger.merged_object_list)


if __name__ == '__main__':
    main()