import sqlite3

# Verbindung herstellen
conn = sqlite3.connect('demo.db')

# Cursor erstellen
cursor = conn.cursor()

# Tabelle anlegen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS names (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age  INTEGER NOT NULL
    )
""")
conn.commit()


# create
cursor.execute("INSERT INTO names(name, age) VALUES (?, ?)",("Alice", 30))


# read
cursor.execute("SELECT id, name, age FROM names ORDER BY ID")
rows = cursor.fetchall()
for row in rows:
    print(row)

# -----------------------------------------------------------------------------
# 6) UPDATE – Bob -> Bobby
# -----------------------------------------------------------------------------
cursor.execute("UPDATE names SET name=? WHERE name=?", ("Bobby", "Bob"))

# -----------------------------------------------------------------------------
# 7) DELETE – lösche Alice
# -----------------------------------------------------------------------------
cursor.execute("DELETE FROM names WHERE name=?", ("Alice",))
conn.commit()

# read
cursor.execute("SELECT id, name, age FROM names ORDER BY ID")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()
print("Verbindung geschlossen.")