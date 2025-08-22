"""
SQLiteSimple.py – Minimalbeispiel für SQLite mit Python

Zeigt Schritt für Schritt:
1) Verbindung + DB-Datei erzeugen
2) Cursor erstellen
3) Tabelle anlegen
4) CRUD: Create, Read, Update, Delete
"""

import sqlite3

# -----------------------------------------------------------------------------
# 1) Verbindung herstellen (Datei wird automatisch angelegt)
# -----------------------------------------------------------------------------
conn = sqlite3.connect("sqlite_demo.db")
print("[OK] Verbunden mit sqlite_demo.db")

# -----------------------------------------------------------------------------
# 2) Cursor erstellen
# -----------------------------------------------------------------------------
cursor = conn.cursor()
print("[OK] Verbunden mit sqlite_demo.db")

# -----------------------------------------------------------------------------
# 3) Tabelle anlegen
# -----------------------------------------------------------------------------
cursor.execute("""
    CREATE TABLE IF NOT EXISTS names (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age  INTEGER NOT NULL
    )
""")
conn.commit()
print("[OK] Tabelle 'names' geprüft/angelegt")

# -----------------------------------------------------------------------------
# 4) CREATE – Datensätze einfügen
# -----------------------------------------------------------------------------
cursor.execute("INSERT INTO names(name, age) VALUES (?, ?)", ("Alice", 30))
cursor.execute("INSERT INTO names(name, age) VALUES (?, ?)", ("Bob", 25))
conn.commit()
print("[OK] CREATE: Alice & Bob eingefügt")

# -----------------------------------------------------------------------------
# 5) READ – alle Datensätze ausgeben
# -----------------------------------------------------------------------------
cursor.execute("SELECT id, name, age FROM names ORDER BY id")
rows = cursor.fetchall()
result = []
for row in rows:
    result.append({"id": row[0], "name": row[1], "age": row[2]})
print("[OK] READ all:", result)

# -----------------------------------------------------------------------------
# 6) UPDATE – Bob -> Bobby
# -----------------------------------------------------------------------------
cursor.execute("UPDATE names SET name=? WHERE name=?", ("Bobby", "Bob"))
conn.commit()
cursor.execute("SELECT id, name, age FROM names ORDER BY id")
rows = cursor.fetchall()
result = []
for row in rows:
    result.append({"id": row[0], "name": row[1], "age": row[2]})
print("[OK] UPDATE: Bob -> Bobby:", result)

# -----------------------------------------------------------------------------
# 7) DELETE – lösche Alice
# -----------------------------------------------------------------------------
cursor.execute("DELETE FROM names WHERE name=?", ("Alice",))
conn.commit()
cursor.execute("SELECT id, name, age FROM names ORDER BY id")
rows = cursor.fetchall()
result = []
for row in rows:
    result.append({"id": row[0], "name": row[1], "age": row[2]})
print("[OK] DELETE: Alice gelöscht:", result)

# -----------------------------------------------------------------------------
# 8) Verbindung schließen
# -----------------------------------------------------------------------------
cursor.close()
conn.close()
print("[OK] Verbindung geschlossen")
