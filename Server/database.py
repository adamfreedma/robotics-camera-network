import sqlite3
from encryption import Encryption
from typing import List, Tuple, Any


class Database:

    def __init__(self, database_name: str):

        self._connect(database_name)
        self.cursor = self.database.cursor()
        self._create_tables()

    def _connect(self, database_name):
        self.database: sqlite3.Connection = sqlite3.connect(database_name, check_same_thread=False)

    def _close(self):
        self.database.close()

    def _create_tables(self):
        create_users_table_statement = f"CREATE TABLE IF NOT EXISTS users(id integer PRIMARY KEY AUTOINCREMENT," \
            f" username text NOT NULL UNIQUE, password text)"
        create_cameras_table_statement = f"CREATE TABLE IF NOT EXISTS cameras(id integer PRIMARY KEY AUTOINCREMENT," \
            f" name text NOT NULL UNIQUE, mac text UNIQUE, x integer NOT NULL, y integer NOT NULL," \
            f" z integer NOT NULL, yaw integer NOT NULL, pitch integer NOT NULL, roll integer NOT NULL)"
        self.cursor.execute(create_users_table_statement)
        self.cursor.execute(create_cameras_table_statement)

    def insert_user(self, username: str, password: str) -> bool:
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
        delete_user_statement = f"DELETE FROM users WHERE username = '{username}'"

        try:
            self.cursor.execute(delete_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def insert_camera(self, name: str, mac: str, x: int, y: int, z: int, yaw: int, pitch: int, roll: int) -> bool:
        insert_user_statement = f"INSERT INTO cameras(name, mac, x, y, z, yaw, pitch, roll) VALUES ('{name}', '{mac}'," \
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
        delete_camera_statement = f"DELETE FROM cameras WHERE mac = '{mac}'"

        try:
            self.cursor.execute(delete_camera_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def update_camera(self, name: str, mac: str, x: int, y: int, z: int, yaw: int, pitch: int, roll: int) -> bool:
        print(name, mac, x, y, z, yaw, pitch, roll)
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

    def update_user(self, username: str, password: str) -> bool:
        print(username, password)
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

    def check_password(self, username: str, password: str) -> bool:
        password = Encryption.hash(password)
        check_login_statement = f"SELECT password FROM users WHERE username = '{username}'"
        self.cursor.execute(check_login_statement)
        output = self.cursor.fetchone()
        result = False
        if output and len(output):
            result = output[0] == password

        return result

    def camera_info(self, mac: str) -> Tuple[str, List[Any]]:
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
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def get_cameras(self) -> List[List[str]]:
        self.cursor.execute("SELECT * FROM cameras")
        return self.cursor.fetchall()


if __name__ == '__main__':
    database = Database("robotics.db")
    database.insert_camera("cam1", "ff:ff:ff:ff:ff:ff", 0, 0, 2, 0, 0, 0)
    database.insert_camera("cam2", "2f:ff:ff:ff:ff:ff", 0, 0, 1, 0, 0, 0)
    if not database.insert_user("adam", "123"):
        print("username already exists")
    print(database.check_password("adam", "123"))
