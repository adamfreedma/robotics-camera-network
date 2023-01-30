import server_connection
import time
import merger

connection = server_connection.Connection(3333)
object_merger = merger.Merger()


while True:

    time.sleep(0.01)

    for msg in connection.incoming_messages:
        object_merger.insert_client_object(msg[0], float(msg[1][:10]), float(msg[1][10:]))

    connection.incoming_messages = []
    print(object_merger.merged_object_list)

