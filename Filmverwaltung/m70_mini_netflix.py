import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g
from m70_movie_service import MovieService
from m70_user_service import UserService
from datetime import datetime

app = Flask(__name__)
DATABASE = 'mini_netflix.db'
movie_service = MovieService(DATABASE)
user_service = UserService(DATABASE)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    movies = movie_service.get_all_movies()
    users = user_service.get_all_users(with_password=True)
    return render_template('home.html', movies=movies, users=users)


@app.route('/movies', methods=['GET'])
def show_movies():
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    movies = movie_service.get_all_movies(sort_by=sort_by, order=order)
    # Für jeden Film alle aktuellen Ausleiher ermitteln
    movie_list = []
    for movie in movies:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT u.username FROM rentals r JOIN users u ON r.user_id = u.id WHERE r.book_id = ? AND r.return_date IS NULL", (movie[0],))
        result = cur.fetchall()
        conn.close()
        ausleiher = [row[0] for row in result] if result else []
        movie_list.append({
            'id': movie[0],
            'title': movie[1],
            'genre': movie[2],
            'likes': movie[3],
            'ausleiher': ausleiher
        })
    return render_template('movies.html', movies=movie_list, sort_by=sort_by, order=order)

@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    error = None
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        if not title or not genre:
            error = 'Bitte füllen Sie alle Pflichtfelder aus.'
            return render_template('add_movie.html', error=error)
        movie_service.add_movie(title, genre)
        return redirect(url_for('show_movies'))
    return render_template('add_movie.html')

@app.route('/like/<int:movie_id>', methods=['POST'])
def like_movie(movie_id):
    movie_service.like_movie(movie_id)
    return redirect(url_for('show_movies'))

@app.route('/rent', methods=['GET', 'POST'])
def rent_movie():
    users = user_service.get_all_users()
    movies = movie_service.get_all_movies()
    error = None
    info = None
    username = None
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        movie_ids = request.form.getlist('movie_id')
        not_rented = []
        rented = []
        if user_id and movie_ids:
            rental_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for movie_id in movie_ids:
                success = user_service.add_rental(user_id, movie_id, rental_date)
                movie = movie_service.get_movie_by_id(movie_id)
                if success:
                    if movie:
                        rented.append(movie[1])
                else:
                    if movie:
                        not_rented.append(movie[1])
            # Nutzername ermitteln
            for user in users:
                if str(user[0]) == str(user_id):
                    username = user[1]
                    break
            # Meldung formatieren
            if rented:
                info = f"verliehen: {', '.join(rented)}"
            if not_rented:
                error = f"bereits ausgeliehen: {', '.join(not_rented)}"
            return render_template('rent.html', users=users, movies=movies, error=error, info=info, username=username)
        else:
            error = 'Bitte Nutzer und mindestens einen Film auswählen.'
            # Nutzername trotzdem ermitteln, falls user_id gesetzt
            if user_id:
                for user in users:
                    if str(user[0]) == str(user_id):
                        username = user[1]
                        break
    return render_template('rent.html', users=users, movies=movies, error=error, info=info, username=username)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    error = None
    user = user_service.get_user_by_id(user_id)
    if request.method == 'POST' and 'return_rental_id' in request.form:
        rental_id = request.form.get('return_rental_id')
        user_service.return_rental(rental_id)
        return redirect(url_for('edit_user', user_id=user_id))
    rentals = user_service.get_rentals_by_user_id(user_id)
    movies = []
    for rental in rentals:
        if rental[3] is None:  # Nur nicht zurückgegebene Filme anzeigen
            movie = movie_service.get_movie_by_id(rental[1])
            if movie:
                movies.append({
                    'title': movie[1],
                    'genre': movie[2],
                    'rental_date': rental[2],
                    'return_date': rental[3],
                    'rental_id': rental[0]
                })
    if not user:
        return redirect(url_for('users'))
    if request.method == 'POST' and 'return_rental_id' not in request.form:
        username = request.form['username']
        password = request.form['password']
        if username and password:
            success = user_service.update_user(user_id, username, password)
            if success:
                return redirect(url_for('users'))
            else:
                error = 'Benutzername existiert bereits.'
        else:
            error = 'Bitte Benutzername und Passwort eingeben.'
    return render_template('edit_user.html', user=user, error=error, movies=movies)

@app.route('/users', methods=['GET', 'POST'])
def users():
    error = None
    username = ''
    password = ''
    # Felder immer leer setzen, auch nach POST
    if request.method == 'POST':
        # Benutzer wird angelegt, Felder bleiben leer
        entered_username = request.form['username']
        entered_password = request.form['password']
        if entered_username and entered_password:
            success = user_service.add_user(entered_username, entered_password)
            if not success:
                error = 'Benutzername existiert bereits.'
        else:
            error = 'Bitte Benutzername und Passwort eingeben.'
    users = user_service.get_all_users(with_password=True)
    return render_template('users.html', users=users, error=error, username=username, password=password)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user_service.delete_user(user_id)
    return redirect(url_for('users'))

@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    error = None
    movie = movie_service.get_movie_by_id(movie_id)
    if not movie:
        return redirect(url_for('show_movies'))
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        if title and genre:
            success = movie_service.update_movie(movie_id, title, genre)
            if success:
                return redirect(url_for('show_movies'))
            else:
                error = 'Fehler beim Speichern.'
        else:
            error = 'Bitte Titel und Genre eingeben.'
    return render_template('edit_movie.html', movie=movie, error=error)

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    movie_service.delete_movie(movie_id)
    return redirect(url_for('show_movies'))

@app.route('/return', methods=['GET', 'POST'])
def return_movie():
    users = user_service.get_all_users()
    movies = movie_service.get_all_movies()
    selected_user_id = request.form.get('user_id') if request.method == 'POST' else request.args.get('user_id')
    error = None
    rentals = []
    if selected_user_id:
        rentals = user_service.get_rentals_by_user_id(selected_user_id)
    if request.method == 'POST' and 'return_rental_id' in request.form:
        rental_id = request.form.get('return_rental_id')
        user_service.return_rental(rental_id)
        return redirect(url_for('return_movie', user_id=selected_user_id))
    return render_template('return.html', users=users, movies=movies, error=error, selected_user_id=selected_user_id, rentals=rentals)

if __name__ == '__main__':
    app.run(debug=True)