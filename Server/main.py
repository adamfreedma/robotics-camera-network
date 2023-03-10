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
            object_merger.insert_client_object(float(msg[1][:10]), float(msg[1][10:]))
        connection.incoming_messages = []
        connection.lock.release()

        gui_object.draw_cones([int(cone[0]) for cone in object_merger.merged_object_list], [int(cone[1]) for cone in object_merger.merged_object_list])


if __name__ == '__main__':
    main()