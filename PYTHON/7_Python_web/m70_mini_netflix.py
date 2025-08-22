# ======================================================================================
# AUFGABE: Mini-„Netflix“ mit Flask
# ======================================================================================
# Ziel:
#   Erstelle eine kleine Webseite, auf der man Filme/Serien
#   eintragen und anzeigen kann.
#
# Anforderungen:
#   1) "/"        : Startseite mit Begrüßung + Buttons zu den Unterseiten
#   2) "/movies"  : Liste aller Filme mit Like-Button + Home-Button
#   3) "/add"     : Formular zum Hinzufügen eines Films + Home-Button
#
# Besondere Herausforderung:
#   füge einen zu jedem Film einen LikeButton und likeCounter hinzu


# ======================================================================================
#                           Mock-Up (Skizzen der einzelnen Seiten)
# ======================================================================================#
# --- Home (/)
# ╔════════════════════════════════════════════╗
# ║              🎬 Mini-Netflix               ║
# ╠════════════════════════════════════════════╣
# ║ Willkommen bei Mini-Netflix!               ║
# ║ Trage eigene Filme ein, gib ihnen ein      ║
# ║ Genre und verteile Likes.                  ║
# ║                                            ║
# ║[📜 Alle Filme]  [➕ Neuen Film hinzufügen] ║
# ╚════════════════════════════════════════════╝
#
# --- Movies (/movies)
# ╔══════════════════════════════════════════╗
# ║              🎬 Mini-Netflix             ║
# ╠══════════════════════════════════════════╣
# ║ Alle Filme                               ║
# ║                                          ║
# ║ ┌──────────────────────────────┐         ║
# ║ │ Akira                • Anime │         ║
# ║ │ 👍 0 [Like]                  │         ║
# ║ └──────────────────────────────┘         ║
# ║                                          ║
# ║ ┌──────────────────────────────┐         ║
# ║ │ The Dark Knight     • Action │         ║
# ║ │ 👍 0 [Like]                  │         ║
# ║ └──────────────────────────────┘         ║
# ║                                          ║
# ║ ┌──────────────────────────────┐         ║
# ║ │ Inception          • Sci-Fi  │         ║
# ║ │ 👍 0 [Like]                  │         ║
# ║ └──────────────────────────────┘         ║
# ║                                          ║
# ║ [🏠 Home]                                ║
# ╚══════════════════════════════════════════╝
#
# --- Add (/add)
# ╔══════════════════════════════════════════╗
# ║              🎬 Mini-Netflix             ║
# ╠══════════════════════════════════════════╣
# ║ Neuen Film hinzufügen                    ║
# ║                                          ║
# ║ Titel: [________________________]        ║
# ║ Genre: [________________________]        ║
# ║                                          ║
# ║ [Speichern]  [🏠 Home]                   ║
# ╚══════════════════════════════════════════╝
