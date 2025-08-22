# Erledige alle todos


import sqlite3

class SQLiteService:

    def __init__(self, db_path: str = "example.db", table: str = "example_table"):
        self.db_path = db_path
        self.table = table
        self.conn = None
        self.cursor = None
        self.__connect()
        self.__ensure_schema()

    def __connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def __close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __ensure_schema(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS animals (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT    NOT NULL,
                age  INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def create(self, name: str, age: int):
        self.cursor.execute("INSERT INTO animals (name, age) VALUES (?, ?)", (name, age))
        self.conn.commit()

    def read_all(self):
        self.cursor.execute("SELECT * FROM animals")
        return self.cursor.fetchall()

    def read_by_id(self, _id: int):
        self.cursor.execute("SELECT * FROM animals WHERE id = ?", (_id,))
        return self.cursor.fetchone()

    def update(self, _id: int, name: str, age: int):
        self.cursor.execute("UPDATE animals SET name = ?, age = ? WHERE id = ?", (name, age, _id))
        self.conn.commit()

    def delete(self, _id: int):
        self.cursor.execute("DELETE FROM animals WHERE id = ?", (_id,))
        self.conn.commit()

    def __del__(self):
        self.__close()

# -----------------------------------------------------------------------------
# main() zum Testen. Wenn der Code fehlerfrei durchläuft, hast du die aufgabe erledigt
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    def zeigeDB(service: SQLiteService):
        rows = service.read_all()
        for row in rows:
            print(row)

    db = SQLiteService()

    # Test: CREATE
    print("Einfügen von Alice und Bob...")
    db.create("Alice", 30)
    db.create("Bob", 25)

    # Test: READ ALL
    print("Alle Datensätze:")
    zeigeDB(db)

    # Test: UPDATE
    print("\nUpdate: Bob -> Bobby...")
    # Hinweis: id muss hier stimmen
    db.update(2, "Bobby", 25)
    zeigeDB(db)

    # Test: DELETE
    print("\nDelete: Alice...")
    db.delete(1)
    zeigeDB(db)
