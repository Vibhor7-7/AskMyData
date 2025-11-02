from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
app = Flask(__name__)
app.secret_key = 'AskMyData'
#home page
@app.route("/")
def index():
    conn=sqlite3.connect('users.db')
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (fullname TEXT NOT NULL,
                username TEXT PRIMARY KEY,
              email TEXT NOT NULL,
                password TEXT NOT NULL)''')
    conn.commit()
    conn.close()
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
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)",
                      (fullname, username, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists. Please choose a different one."
        finally:
            conn.close()
        return render_template("logged_in_home.html", username=username)
    else:
        return render_template("register.html")


print("App is running...")
if __name__ == "__main__":
    app.run()