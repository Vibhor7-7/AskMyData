from flask import Flask, render_template

app = Flask(__name__)
#home page
@app.route("/")
def index():
    return render_template("index.html")

print("App is running...")
if __name__ == "__main__":
    app.run()