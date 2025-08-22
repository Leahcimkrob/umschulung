import sqlite3

class MovieService:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_movies(self, sort_by='title', order='asc'):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Sicherheitscheck für sort_by und order
        if sort_by not in ['title', 'genre']: sort_by = 'title'
        if order not in ['asc', 'desc']: order = 'asc'
        if sort_by == 'genre':
            query = f"SELECT id, title, genre, likes FROM movies ORDER BY genre {order}, title ASC"
        else:
            query = f"SELECT id, title, genre, likes FROM movies ORDER BY title {order}"
        cur.execute(query)
        movies = cur.fetchall()
        conn.close()
        return movies

    def add_movie(self, title, genre):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO movies (title, genre) VALUES (?, ?)", (title, genre))
        conn.commit()
        conn.close()

    def like_movie(self, movie_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE movies SET likes = likes + 1 WHERE id = ?", (movie_id,))
        conn.commit()
        conn.close()

    def get_movie_by_id(self, movie_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, title, genre, likes FROM movies WHERE id = ?", (movie_id,))
        movie = cur.fetchone()
        conn.close()
        return movie

    def update_movie(self, movie_id, title, genre):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute("UPDATE movies SET title = ?, genre = ? WHERE id = ?", (title, genre, movie_id))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return False
        conn.close()
        return True

    def delete_movie(self, movie_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        conn.commit()
        conn.close()
