import sqlite3
from encryption import Encryption
from typing import List, Tuple, Any


class Database:

    def __init__(self, database_name: str):

        self._connect(database_name)
        self.cursor = self.database.cursor()
        self._create_tables()

    def _connect(self, database_name: str):
        """
        connects to the database
        :param database_name: database path
        """
        self.database: sqlite3.Connection = sqlite3.connect(database_name, check_same_thread=False)

    def _close(self):
        """
        closes the database
        """
        self.database.close()

    def _create_tables(self):
        """
        creates the tables with the correct columns if they are not created yet
        """
        create_users_table_statement = f"CREATE TABLE IF NOT EXISTS users(id integer PRIMARY KEY AUTOINCREMENT," \
            f" username text NOT NULL UNIQUE, password text)"
        create_cameras_table_statement = f"CREATE TABLE IF NOT EXISTS cameras(id integer PRIMARY KEY AUTOINCREMENT," \
            f" name text NOT NULL UNIQUE, mac text UNIQUE, x integer NOT NULL, y integer NOT NULL," \
            f" z integer NOT NULL, yaw integer NOT NULL, pitch integer NOT NULL, roll integer NOT NULL)"
        self.cursor.execute(create_users_table_statement)
        self.cursor.execute(create_cameras_table_statement)

    def insert_user(self, username: str, password: str) -> bool:
        """
        inserts a user into the database
        :param username: user's username
        :param password: user's password
        :return: was the insertion successful
        """
        password = Encryption.hash(password)
        insert_user_statement = f"INSERT INTO users(username, password) VALUES ('{username}', '{password}')"

        try:
            self.cursor.execute(insert_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def delete_user(self, username: str) -> bool:
        """
        deletes a user
        :param username: user's username to delete
        :return: was the deletion successful
        """
        delete_user_statement = f"DELETE FROM users WHERE username = '{username}'"

        try:
            self.cursor.execute(delete_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def update_user(self, username: str, password: str) -> bool:
        """
        updates a user in the database
        :param username: user's username
        :param password: user's password
        :return: was the update successful
        """
        password = Encryption.hash(password)
        update_user_statement = f"UPDATE users SET password = '{password}' WHERE username = '{username}'"

        try:
            self.cursor.execute(update_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def insert_camera(self, name: str, mac: str, x: float, y: float, z: float, yaw: float, pitch: float, roll: float)\
            -> bool:
        """
        inserts a camera into the database
        :param name: camera name
        :param mac: camera mac
        :param x: camera x
        :param y: camera y
        :param z: camera z
        :param yaw: camera yaw
        :param pitch: camera pitch
        :param roll: camera roll
        :return: was the insertion successful
        """
        insert_user_statement = f"INSERT INTO cameras(name, mac, x, y, z, yaw, pitch, roll) VALUES ('{name}', '{mac}',"\
            f" '{x}', '{y}', '{z}', '{yaw}', '{pitch}', '{roll}')"

        try:
            self.cursor.execute(insert_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def delete_camera(self, mac: str) -> bool:
        """
        inserts a camera
        :param mac: camera's mac to delete
        :return: was the deletion successful
        """
        delete_camera_statement = f"DELETE FROM cameras WHERE mac = '{mac}'"

        try:
            self.cursor.execute(delete_camera_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def update_camera(self, name: str, mac: str, x: float, y: float, z: float, yaw: float, pitch: float, roll: float)\
            -> bool:
        """
        updates the camera in the database
        :param name: camera name
        :param mac: camera mac
        :param x: camera x
        :param y: camera y
        :param z: camera z
        :param yaw: camera yaw
        :param pitch: camera pitch
        :param roll: camera roll
        :return: was the update successful
        """
        update_camera_statement = f"UPDATE cameras SET name = '{name}', x = '{x}', y = '{y}', z = '{z}'," \
            f" yaw = '{yaw}', pitch = '{pitch}', roll = '{roll}' WHERE mac = '{mac}'"

        try:
            self.cursor.execute(update_camera_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def check_password(self, username: str, password: str) -> bool:
        """
        checks whether the user credentials are correct
        :param username: user's username
        :param password: user's password
        :return: are the credentials correct
        """
        password = Encryption.hash(password)
        check_login_statement = f"SELECT password FROM users WHERE username = '{username}'"
        self.cursor.execute(check_login_statement)
        output = self.cursor.fetchone()
        result = False
        if output and len(output):
            result = output[0] == password

        return result

    def camera_info(self, mac: str) -> Tuple[str, List[Any]]:
        """
        gets info about a camera from the database
        :param mac: camera mac
        :return: name, ((x, y, z), (yaw, pitch, roll))
        """
        camera_name_statement = f"SELECT name FROM cameras WHERE mac = '{mac}'"
        self.cursor.execute(camera_name_statement)

        name = ""
        output = self.cursor.fetchone()
        if output and len(output):
            name = output[0]

        camera_location_statement = f"SELECT x, y, z, yaw, pitch, roll FROM cameras WHERE mac = '{mac}'"
        self.cursor.execute(camera_location_statement)

        location = self.cursor.fetchone()

        return name, location

    def get_users(self) -> List[List[str]]:
        """
        gets all users data
        :return: list of users
        """
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def get_cameras(self) -> List[List[str]]:
        """
        gets all cameras data
        :return: list of cameras
        """
        self.cursor.execute("SELECT * FROM cameras")
        return self.cursor.fetchall()


if __name__ == '__main__':
    database = Database("robotics.db")
    database.insert_camera("cam1", "ff:ff:ff:ff:ff:ff", 0, 0, 2, 0, 0, 0)
    database.insert_camera("cam2", "2f:ff:ff:ff:ff:ff", 0, 0, 1, 0, 0, 0)
    if not database.insert_user("adam", "123"):
        print("username already exists")
    print(database.check_password("adam", "123"))
