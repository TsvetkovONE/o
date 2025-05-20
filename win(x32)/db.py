import pymysql

class Database:
    def __init__(self):
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='primer',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_cursor(self):
        return self.connection.cursor()

    def execute_query(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            if query.strip().lower().startswith(("insert", "update", "delete")):
                self.connection.commit()
            return cursor.fetchall()

    def close(self):
        self.connection.close()
