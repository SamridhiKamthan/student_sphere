from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "studentsphere"

DATABASE = "studentsphere.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS internships(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username, password)
            )
            conn.commit()
            return redirect(url_for("login"))

        except:
            return "Username already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return "Invalid Credentials"

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":

        form_type = request.form.get("form_type")

        if form_type == "project":

            title = request.form["title"]
            description = request.form["description"]

            conn.execute(
                "INSERT INTO projects(title,description) VALUES (?,?)",
                (title, description)
            )

        elif form_type == "internship":

            company = request.form["company"]
            status = request.form["status"]

            conn.execute(
                "INSERT INTO internships(company,status) VALUES (?,?)",
                (company, status)
            )

        conn.commit()

    projects = conn.execute("SELECT * FROM projects").fetchall()
    internships = conn.execute("SELECT * FROM internships").fetchall()

    return render_template(
        "dashboard.html",
        projects=projects,
        internships=internships,
        user=session["user"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)                      
