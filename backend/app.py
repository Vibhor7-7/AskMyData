from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import io
import json
import pandas as pd
from icalendar import Calendar

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Set up paths
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')
db_path = os.path.join(current_dir, 'users.db')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)
app.secret_key = 'AskMyData'
#home page
@app.route("/")
def index():
    conn=sqlite3.connect(db_path)
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
    if "username" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row is None or not check_password_hash(row[0], password):
            return "Invalid username or password"
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
    if "username" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)",
                      (fullname, username, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists. Please choose a different one."
        finally:
            conn.close()
        session["username"] = username
        return render_template("logged_in_home.html", username=username)
    else:
        return render_template("register.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return "No file uploaded", 400

        filename = file.filename
        fname = filename.lower()
        info = {}

        try:
            if fname.endswith(".csv"):
                # read bytes -> string -> pandas
                content = file.stream.read()
                text = content.decode("utf-8", errors="replace")
                df = pd.read_csv(io.StringIO(text))
                info["type"] = "csv"
                info["num_rows"] = len(df)
                info["num_cols"] = len(df.columns)
                info["columns"] = df.columns.tolist()

            elif fname.endswith(".json"):
                content = file.stream.read()
                data = json.loads(content.decode("utf-8"))
                info["type"] = "json"
                if isinstance(data, list):
                    info["items"] = len(data)
                    info["sample"] = data[0] if data else None
                elif isinstance(data, dict):
                    info["keys"] = list(data.keys())
                else:
                    info["json_type"] = type(data).__name__

            elif fname.endswith(".ics"):
                content = file.stream.read()
                cal = Calendar.from_ical(content)
                events = [c for c in cal.walk() if c.name == "VEVENT"]
                info["type"] = "ics"
                info["num_events"] = len(events)
                if events:
                    first = events[0]
                    info["first_summary"] = str(first.get("summary"))
                    dtstart = first.get("dtstart")
                    if dtstart:
                        info["first_start"] = str(dtstart.dt)

            else:
                return "Unsupported file type. Allowed: .csv, .json, .ics", 400

        except Exception as e:
            return f"Error processing file: {e}", 500

        # pass filename + info to questions page (no saving)
        return render_template("questions.html", filename=filename, info=info)

    return render_template("upload.html")

if __name__ == "__main__":
    print("App is running...")
    app.run(debug=True)