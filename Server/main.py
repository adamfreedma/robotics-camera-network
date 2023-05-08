import server_connection
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

        # adds received cones to the merger
        for msg in connection.incoming_messages:
            x, y = connection.unpack_protocol(msg[1])
            object_merger.insert_client_object(x, y)

        connection.incoming_messages = []

        connection.lock.release()

        # sends merged cones to the gui
        object_merger.lock.acquire()
        pub.sendMessage("cones_list", cones=object_merger.merged_object_list.copy())
        object_merger.lock.release()


def handle_login_request(username: str, password: str):
    """
    check the user's credentials and sends ack/rej respectively
    :param username: user's username
    :param password: user's password
    """
    accepted = database.check_password(username, password)

    if accepted:
        pub.sendMessage("login_answer", answer="ack")
    else:
        pub.sendMessage("login_answer", answer="rej")


def handle_refresh_request():
    """
    sends the users and cameras list to the gui
    """
    users_list = database.get_users()
    pub.sendMessage("users_list", users_list=users_list)
    
    cameras_list = database.get_cameras()
    pub.sendMessage("cameras_list", cameras_list=cameras_list)


def handle_delete_user(username: str):
    """
    deletes a user from the data
    :param username: the username of the user to delete
    """
    database.delete_user(username)


def handle_delete_camera(mac: str):
    """
    deletes a camera from the data
    :param mac: the mac of the camera to delete
    """
    database.delete_camera(mac)


def handle_direction(direction: str):
    """
    sends a movement direction to the robot
    :param direction: the direction to send
    """
    robot_conn.update_direction(direction)


def handle_create_user(username: str, password: str):
    """
    inserts a user into the database and sends back S/F if it succeeded or failed (username taken)
    :param username: user's username
    :param password: user's password
    """
    if database.insert_user(username, password):
        pub.sendMessage("create_user_answer", answer="S")
    else:
        pub.sendMessage("create_user_answer", answer="F")


def handle_edit_user(username: str, password: str):
    """
    updates a user in the database and sends back S/F if it succeeded or failed (username doesn't exists)
    :param username: user's username
    :param password: user's password
    """
    if database.update_user(username, password):
        pub.sendMessage("edit_user_answer", answer="S")
    else:
        pub.sendMessage("edit_user_answer", answer="F")


def handle_create_camera(name: str, mac: str, x: float, y: float, z: float, yaw: float, pitch: float, roll: float):
    """
    inserts a camera into the database and sends back S/F if it succeeded or failed (mac taken)
   :param name: camera name
    :param mac: camera mac
    :param x: camera x
    :param y: camera y
    :param z: camera z
    :param yaw: camera yaw
    :param pitch: camera pitch
    :param roll: camera roll
    """
    if database.insert_camera(name, mac, x, y, z, yaw, pitch, roll):
        pub.sendMessage("create_camera_answer", answer="S")
    else:
        pub.sendMessage("create_camera_answer", answer="F")


def handle_edit_camera(name: str, mac: str, x: float, y: float, z: float, yaw: float, pitch: float, roll: float):
    """
    updates a camera in the database and sends back S/F if it succeeded or failed (mac doesn't exist)
    :param name: camera name
    :param mac: camera mac
    :param x: camera x
    :param y: camera y
    :param z: camera z
    :param yaw: camera yaw
    :param pitch: camera pitch
    :param roll: camera roll
    """
    if database.update_camera(name, mac, x, y, z, yaw, pitch, roll):
        pub.sendMessage("edit_camera_answer", answer="S")
    else:
        pub.sendMessage("edit_camera_answer", answer="F")


def main():
    main_server_thread = threading.Thread(target=main_server, args=[], daemon=True)
    main_server_thread.start()

    # subscribe handlers
    pub.subscribe(handle_login_request, "login_request")
    pub.subscribe(handle_refresh_request, "refresh_request")
    pub.subscribe(handle_direction, "direction")
    pub.subscribe(handle_delete_user, "delete_user")
    pub.subscribe(handle_create_user, "create_user")
    pub.subscribe(handle_edit_user, "edit_user")
    pub.subscribe(handle_delete_camera, "delete_camera")
    pub.subscribe(handle_create_camera, "create_camera")
    pub.subscribe(handle_edit_camera, "edit_camera")

    gui.MainFrame()
    gui.app.MainLoop()


if __name__ == '__main__':
    main()
