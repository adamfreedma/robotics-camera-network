import sqlite3
from encryption import Encryption
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
            f" name text NOT NULL UNIQUE, mac text UNIQUE)"
        self.cursor.execute(create_users_table_statement)
        self.cursor.execute(create_cameras_table_statement)

    def insert_user(self, username: str, password: str):
        password = Encryption.hash(password)
        try:
            insert_user_statement = f"INSERT into users(username, password) VALUES ('{username}', '{password}')"
            self.cursor.execute(insert_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def insert_camera(self, name: str, mac: str):
        try:
            insert_user_statement = f"INSERT into cameras(name, mac) VALUES ('{name}', '{mac}')"
            self.cursor.execute(insert_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def update_camera(self, name: str, mac: str):
        try:
            insert_user_statement = f"UPDATE users SET password = '{name}' WHERE username = '{mac}'"
            self.cursor.execute(insert_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def update_user(self, username: str, password: str):
        password = Encryption.hash(password)
        try:
            insert_user_statement = f"UPDATE users SET password = '{password}' WHERE username = '{username}'"
            self.cursor.execute(insert_user_statement)
            self.database.commit()
        except sqlite3.IntegrityError:
            success = False
        else:
            success = True

        return success

    def check_password(self, username: str, password: str):
        password = Encryption.hash(password)
        check_login_statement = f"SELECT password FROM users WHERE username = '{username}'"
        self.cursor.execute(check_login_statement)
        output = self.cursor.fetchone()
        result = False
        if output and len(output):
            result = output[0] == password

        return result

    def camera_name(self, mac: str):
        camera_exists_statement = f"SELECT name FROM cameras WHERE mac = '{mac}'"
        self.cursor.execute(camera_exists_statement)
        name = ""
        output = self.cursor.fetchone()
        if output and len(output):
            name = output[0]
        return name

    def _query_all(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()


if __name__ == '__main__':
    database = Database("test.db")
    if not database.insert_user("adam6", "123"):
        print("username already exists")
    print(database.check_password("adam5", "123"))
