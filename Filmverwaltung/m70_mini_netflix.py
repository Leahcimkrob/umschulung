import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, g, session
from m70_movie_service import MovieService
from m70_user_service import UserService
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supergeheim'  # Für Session
DATABASE = 'mini_netflix.db'
movie_service = MovieService(DATABASE)
user_service = UserService(DATABASE)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_service.get_user_by_username(username)
        if user and user[2] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Login fehlgeschlagen!'
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    movies = movie_service.get_all_movies()
    users = user_service.get_all_users(with_password=True)
    user = user_service.get_user_by_username(session['username']) if 'username' in session else None
    is_admin = user[3] if user else 0
    return render_template('home.html', movies=movies, users=users, is_admin=is_admin)


@app.route('/movies', methods=['GET'])
@login_required
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
@login_required
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
        # Direktes Ausleihen aus der Filmliste (nur ein Film, aktueller User)
        if request.form.get('movie_id') and request.form.get('user_id'):
            movie_id = request.form.get('movie_id')
            user_name = request.form.get('user_id')
            user_obj = user_service.get_user_by_username(user_name)
            if user_obj:
                user_id = user_obj[0]
                rental_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                success = user_service.add_rental(user_id, movie_id, rental_date)
                movie = movie_service.get_movie_by_id(movie_id)
                if success:
                    info = f"Film '{movie[1]}' erfolgreich ausgeliehen."
                else:
                    error = f"Film '{movie[1]}' ist bereits ausgeliehen."
                return redirect(url_for('show_movies'))
        # Standard-Ausleihen (mehrere Filme, Auswahl)
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
        is_admin = 1 if request.form.get('is_admin') == '1' else 0
        allowed_pattern = r'^[A-Za-z0-9_#+!"§$%&/()?=.,:;Q]+$'
        if ' ' in username:
            error = 'Benutzernamen dürfen keine Leerzeichen enthalten.'
        elif not re.match(allowed_pattern, username):
            error = 'Benutzername enthält nicht erlaubte Zeichen.'
        elif username and password:
            success = user_service.update_user(user_id, username, password, is_admin)
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
    if request.method == 'POST':
        entered_username = request.form['username']
        entered_password = request.form['password']
        is_admin = 1 if request.form.get('is_admin') == '1' else 0
        allowed_pattern = r'^[A-Za-z0-9_#+!"§$%&/()?=.,:;Q]+$'
        if ' ' in entered_username:
            error = 'Benutzernamen dürfen keine Leerzeichen enthalten.'
        elif not re.match(allowed_pattern, entered_username):
            error = 'Benutzername enthält nicht erlaubte Zeichen.'
        elif entered_username and entered_password:
            success = user_service.add_user(entered_username, entered_password, is_admin)
            if not success:
                error = 'Benutzername existiert bereits.'
        else:
            error = 'Bitte Benutzername und Passwort eingeben.'
    users = user_service.get_all_users(with_password=True)
    return render_template('users.html', users=users, error=error, username=username, password=password)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    error = None
    user = None
    movies = []
    if 'username' in session:
        user = user_service.get_user_by_username(session['username'])
        rentals = user_service.get_rentals_by_user_id(user[0])
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
    if request.method == 'POST':
        if 'return_rental_id' in request.form:
            rental_id = request.form.get('return_rental_id')
            user_service.return_rental(rental_id)
            return redirect(url_for('profile'))
        entered_username = request.form.get('username')
        entered_password = request.form.get('password')
        allowed_pattern = r'^[A-Za-z0-9_#+!"§$%&/()?=.,:;Q]+$'
        if ' ' in entered_username:
            error = 'Benutzernamen dürfen keine Leerzeichen enthalten.'
        elif not re.match(allowed_pattern, entered_username):
            error = 'Benutzername enthält nicht erlaubte Zeichen.'
        elif entered_username and entered_password:
            # Profil-Update: Nur für eigenen User
            success = user_service.update_user(user[0], entered_username, entered_password, user[3])
            if success:
                user = user_service.get_user_by_username(entered_username)
                session['username'] = entered_username
            else:
                error = 'Benutzername existiert bereits.'
        else:
            error = 'Bitte Benutzername und Passwort eingeben.'
    return render_template('profile.html', user=user, error=error, movies=movies)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user_service.delete_user(user_id)
    return redirect(url_for('users'))

@app.route('/edit_movie', methods=['GET', 'POST'])
def edit_movie():
    error = None
    success = None
    movie_id = request.args.get('movie_id', type=int)
    movies = movie_service.get_all_movies()  # Liefert Liste aller Filme
    movie = None
    if movie_id:
        movie = movie_service.get_movie_by_id(movie_id)
    if request.method == 'POST' and movie_id:
        title = request.form['title']
        genre = request.form['genre']
        if title and genre:
            update_success = movie_service.update_movie(movie_id, title, genre)
            if update_success:
                success = 'Film erfolgreich gespeichert.'
                # Bleibt auf der Seite, zeigt Erfolgsmeldung
                movie = movie_service.get_movie_by_id(movie_id)
            else:
                error = 'Fehler beim Speichern.'
        else:
            error = 'Bitte Titel und Genre eingeben.'
    return render_template('edit_movie.html', movies=movies, movie=movie, movie_id=movie_id, error=error, success=success)

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        allowed_pattern = r'^[A-Za-z0-9_#+!"§$%&/()?=.,:;Q]+$'
        if ' ' in username:
            error = 'Benutzernamen dürfen keine Leerzeichen enthalten.'
        elif not re.match(allowed_pattern, username):
            error = 'Benutzername enthält nicht erlaubte Zeichen.'
        elif username and password:
            # Standardmäßig kein Admin
            success = user_service.add_user(username, password, 0)
            if success:
                return redirect(url_for('login'))
            else:
                error = 'Benutzername existiert bereits.'
        else:
            error = 'Bitte Benutzername und Passwort eingeben.'
    return render_template('register.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)