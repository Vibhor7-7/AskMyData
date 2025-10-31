from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
app = Flask(__name__)
app.secret_key = 'AskMyData'
#home page
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Need to add verification
        print(username)
        session["username"] = username
        return render_template("logged_in_home.html", username=username)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/home")
def home():
    if "username" in session:
        username = session["username"]
        return render_template("logged_in_home.html", username=username)
    else:
        return redirect(url_for("login"))


print("App is running...")
if __name__ == "__main__":
    app.run()