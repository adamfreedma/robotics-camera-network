import sqlite3


class Database:

    def __init__(self, database_name: str):

        self._connect(database_name)
        self.cursor = self.database.cursor()
        self._create_table()

    def _connect(self, database_name):
        self.database: sqlite3.Connection = sqlite3.connect(database_name)

    def _close(self):
        self.database.close()

    def _create_table(self):
        create_table_statement = f"CREATE TABLE IF NOT EXISTS users(id integer  PRIMARY KEY AUTOINCREMENT," \
            f" username text, password text)"
        self.cursor.execute(create_table_statement)

    def check_login(self, username: str, password: str):

        check_login_statement = f"SELECT password FROM users WHERE username = '{username}'"
        self.cursor.execute(check_login_statement)
        output = self.cursor.fetchone()
        result = False
        if output and len(output):
            result = output[0] == password

        return result




if __name__ == '__main__':
    database = Database("test.db")
    print(database.check_login("admin", "123"))
