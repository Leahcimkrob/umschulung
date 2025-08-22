from flask import Flask
from flask import url_for

app = Flask(__name__)

@app.route("/")
def home():
    return f"""
    <h1>Hello World – meine erste Flask-Seite!</h1>
    <nav>
      <a href="{url_for('about')}">About</a> |
      <a href="{url_for('contact')}">Contact</a>
    </nav>
    """

@app.route("/about")
def about():
    return f"""
    <h1>Über diese Seite: Flask-Demo.</h1>
    <nav>
      <a href="{url_for('home')}">Home</a> |
      <a href="{url_for('contact')}">Contact</a>
    </nav>
    """

@app.route("/contact")
def contact():
    return f"""
    <h1>Kontakt: demo@example.com</h1>
    <nav>
      <a href="{url_for('home')}">Home</a> |
      <a href="{url_for('about')}">About</a>
    </nav>
    """

if __name__ == "__main__":
    app.run(debug=True)
