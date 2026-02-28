from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

# ---------------------------
# DATABASE SETUP
# ---------------------------
def init_db():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll INTEGER,
            name TEXT,
            marks REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Create default admin if not exists
    c.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not c.fetchone():
        hashed = generate_password_hash("admin123", method='pbkdf2:sha256')

        c.execute("INSERT INTO users (username, password) VALUES (?,?)",
                  ("admin", hashed))

    conn.commit()
    conn.close()

init_db()

# ---------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------
def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ---------------------------
# LOGIN
# ---------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("students.db")
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect("/")
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------------
# DASHBOARD
# ---------------------------
@app.route("/")
@login_required
def index():
    search = request.args.get("search")

    conn = sqlite3.connect("students.db")
    c = conn.cursor()

    if search:
        c.execute("SELECT * FROM students WHERE roll LIKE ? OR name LIKE ?",
                  (f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT * FROM students")

    students = c.fetchall()

    # Stats
    c.execute("SELECT COUNT(*), AVG(marks) FROM students")
    stats = c.fetchone()

    conn.close()

    total = stats[0]
    avg = round(stats[1],2) if stats[1] else 0

    return render_template("index.html",
                           students=students,
                           total=total,
                           avg=avg)

# ---------------------------
# ADD
# ---------------------------
@app.route("/add", methods=["GET","POST"])
@login_required
def add():
    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"]
        marks = request.form["marks"]

        conn = sqlite3.connect("students.db")
        c = conn.cursor()
        c.execute("INSERT INTO students (roll,name,marks) VALUES (?,?,?)",
                  (roll,name,marks))
        conn.commit()
        conn.close()

        flash("Student added successfully!", "success")
        return redirect("/")

    return render_template("add.html")

# ---------------------------
# EDIT
# ---------------------------
@app.route("/edit/<int:id>", methods=["GET","POST"])
@login_required
def edit(id):
    conn = sqlite3.connect("students.db")
    c = conn.cursor()

    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"]
        marks = request.form["marks"]

        c.execute("UPDATE students SET roll=?, name=?, marks=? WHERE id=?",
                  (roll,name,marks,id))
        conn.commit()
        conn.close()

        flash("Student updated successfully!", "warning")
        return redirect("/")

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()
    conn.close()

    return render_template("edit.html", student=student)

# ---------------------------
# DELETE
# ---------------------------
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("Student deleted successfully!", "danger")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
