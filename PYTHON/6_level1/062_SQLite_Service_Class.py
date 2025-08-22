import sqlite3

class SQLiteService:
    def __init__(self, db_path: str = "sqlite_demo.db", table: str = "example_table"):
        self.db_path = db_path
        self.table = table
        self.conn = None
        self.cursor = None
        self.__connect()
        self.__ensure_schema()
        self.__close()


    def __connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()


    def __close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None


    def __ensure_schema(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT    NOT NULL,
                age  INTEGER NOT NULL
            )
        """)
        self.conn.commit()


    def create(self, name: str, age: int) -> int:
        self.__connect()
        self.cursor.execute(
            f"INSERT INTO {self.table} (name, age) VALUES (?, ?)", (name, age)
        )
        self.conn.commit()
        last_id = self.cursor.lastrowid
        self.__close()
        return last_id


    def read_all(self):
        self.__connect()
        self.cursor.execute(f"SELECT id, name, age FROM {self.table} ORDER BY id")
        rows = self.cursor.fetchall()
        self.__close()
        result = []
        for r in rows:
            result.append({"id": r[0], "name": r[1], "age": r[2]})
        return result


    def read_by_id(self, _id: int):
        self.__connect()
        self.cursor.execute(
            f"SELECT id, name, age FROM {self.table} WHERE id = ?", (_id,)
        )
        row = self.cursor.fetchone()
        self.__close()

        if row is None:
            return None

        result = {"id": row[0], "name": row[1], "age": row[2]}
        return result


    def update(self, _id: int, *, name=None, age=None) -> int:
        self.__connect()
        sets, vals = [], []
        if name is not None:
            sets.append("name = ?")
            vals.append(name)
        if age is not None:
            sets.append("age = ?")
            vals.append(age)
        if not sets:
            self.__close()
            return 0
        vals.append(_id)
        sql = f"UPDATE {self.table} SET {', '.join(sets)} WHERE id = ?"
        self.cursor.execute(sql, tuple(vals))
        self.conn.commit()
        count = self.cursor.rowcount
        self.__close()
        return count

    def delete(self, _id: int) -> int:
        self.__connect()
        self.cursor.execute(f"DELETE FROM {self.table} WHERE id = ?", (_id,))
        self.conn.commit()
        count = self.cursor.rowcount
        self.__close()
        return count


def main():
    sqlite_service = SQLiteService()
    a:int = sqlite_service.create("John", 25)
    b:int = sqlite_service.create("Jane", 30)
    c:int = sqlite_service.create("Bob", 35)
    print("Nach CREATE:", sqlite_service.read_all())
    print("READ by id:", sqlite_service.read_by_id(b))
    sqlite_service.update(c, age=36, name="Bobby")
    print("Nach UPDATE:", sqlite_service.read_all())
    sqlite_service.delete(a)
    print("Nach DELETE:", sqlite_service.read_all())


if __name__ == "__main__":
    main()
