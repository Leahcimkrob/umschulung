"""
┌───────────────┐       HTTP-Request       ┌──────────────┐
│   Browser     │ ───────────────────────▶ │   Server     │
│ (Chrome, FF)  │                          │ (Flask-App)  │
└───────────────┘       HTTP-Response      └──────────────┘
        ▲  ◀───────────────────────────────┘
        │
        │  HTML wird angezeigt
        ▼
   Webseite sichtbar


- Browser stellt eine Anfrage (GET / URL).
- Server (Flask) beantwortet mit HTML.
- Browser zeigt Seite an.
- Flask = unser Werkzeug, um den Server zu bauen.
"""


# Flask importieren
from flask import Flask

# Eine Flask-Instanz erzeugen
# __name__ sagt Flask, wo die App läuft (damit es Dateien/Module findet)
app = Flask(__name__)

# Route definieren: "/" bedeutet Startseite
@app.route("/")
def home():
    # Was hier zurückkommt, sieht man im Browser
    return "<h1>Hallo Welt! 🎉</h1><p>Meine erste Flask-Seite.</p>"

# Nur starten, wenn das Script direkt ausgeführt wird
if __name__ == "__main__":
    # debug=True = zeigt Fehlerdetails, reloadet automatisch bei Änderungen
    app.run(debug=True)

# Running on http://127.0.0.1:5000/