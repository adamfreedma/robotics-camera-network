import server_connection
import time
import merger
import gui
import threading
import database
import robot_connection
from pubsub import pub

database = database.Database("robotics.db")
robot_conn = robot_connection.RobotConnection()
connection = server_connection.Connection(3333)
object_merger = merger.Merger()


def main_server():

    while True:
        connection.lock.acquire()
        
        for msg in connection.incoming_messages:
            x, y = connection.unpack_protocol(msg[1])
            object_merger.insert_client_object(x, y)

        connection.incoming_messages = []

        connection.lock.release()

        object_merger.lock.acquire()
        pub.sendMessage("cones_list", cones=object_merger.merged_object_list.copy())
        object_merger.lock.release()


def handle_login_request(username, password):
    accepted = database.check_password(username, password)

    if accepted:
        pub.sendMessage("login_answer", answer="ack")
    else:
        pub.sendMessage("login_answer", answer="rej")


def handle_refresh_request():
    users_list = database.get_users()
    pub.sendMessage("users_list", users_list=users_list)
    
    cameras_list = database.get_cameras()
    pub.sendMessage("cameras_list", cameras_list=cameras_list)


def handle_delete_user(username):
    database.delete_user(username)


def handle_delete_camera(mac):
    database.delete_camera(mac)


def handle_direction_change(direction):
    robot_conn.update_direction(direction)


def main():
    main_server_thread = threading.Thread(target=main_server, args=[], daemon=True)
    main_server_thread.start()

    pub.subscribe(handle_login_request, "login_request")
    pub.subscribe(handle_refresh_request, "refresh_request")
    pub.subscribe(handle_direction_change, "direction")
    pub.subscribe(handle_delete_camera, "delete_camera")
    pub.subscribe(handle_delete_user, "delete_user")

    main_frame = gui.MainFrame()
    gui.app.MainLoop()


if __name__ == '__main__':
    main()
