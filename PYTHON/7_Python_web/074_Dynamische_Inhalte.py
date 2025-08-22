from flask import Flask, render_template, redirect, url_for
from pygments.lexers import q

app = Flask(__name__)

name = "Alice"
users = ["Alice", "Bob", "Charlie", "Charlie"]
visible = False





@app.route("/")
def home():
    return render_template("users.html", title="Users", users=users, visible=visible, name=name)

@app.route("/toggle")
def toggle():
    global visible
    visible = not visible
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
