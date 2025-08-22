from flask import Flask, render_template, url_for

app = Flask(__name__)



# Startseite
@app.route("/")
def home():
    return render_template("home.html", title="Home")

# About-Seite
@app.route("/about")
def about():
    return render_template("about.html", title="About")

# Contact-Seite
@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")

if __name__ == "__main__":
    app.run(debug=True)
