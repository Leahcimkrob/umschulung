"""
1.) erstelle mittels python eine SQLite-Verbindung
2.) erstelle mittels der SQLite-Verbindung die Tabelle "names", die Attribute id und name hat.
3.) füge der Tabelle 3 Einträge hinzu
4.) verändere den 3ten Eintrag
5.) lösche den letzten Eintrag
6.) mach alles in der Console sichtbar mittels print-Befehlen
"""

import sqlite3

# 1. Verbindung herstellen
conn = sqlite3.connect('m60.db')
cursor = conn.cursor()

# 2. Tabelle erstellen
cursor.execute('CREATE TABLE IF NOT EXIsts names (id INTEGER PRIMARY KEY, name TEXT)')
print("Tabelle erstellt.")

# 3. Drei Einträge hinzufügen
names = ['Anna', 'Bernd', 'Clara']
for name in names:
    cursor.execute('INSERT INTO names (name) VALUES (?)', (name,))
print("Drei Einträge hinzugefügt:")
for row in cursor.execute('SELECT * FROM names'):
    print(row)

# 4. Dritten Eintrag ändern
cursor.execute('UPDATE names SET name = ? WHERE id = 3', ('Carla',))
print("Dritter Eintrag geändert:")
for row in cursor.execute('SELECT * FROM names'):
    print(row)

# 5. Letzten Eintrag löschen
cursor.execute('DELETE FROM names WHERE id = (SELECT MAX(id) FROM names)')
print("Letzten Eintrag gelöscht:")
for row in cursor.execute('SELECT * FROM names'):
    print(row)

# Verbindung schließen
cursor.close()
conn.close()
print("Verbindung geschlossen.")