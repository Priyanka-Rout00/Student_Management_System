
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Connect to database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create student table
def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home page - display students and search
@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    students = conn.execute(
        """SELECT * FROM students
        WHERE name LIKE ? OR email LIKE ?
        OR course LIKE ? OR phone LIKE ?
        ORDER BY id DESC""",
        (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%")
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        students=students,
        search=search
    )


# Add student
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()
        phone = request.form["phone"].strip()

        if not all([name, email, course, phone]):
            return "All fields are required!", 400

        conn = get_db_connection()

        conn.execute(
            """INSERT INTO students (name, email, course, phone)
            VALUES (?, ?, ?, ?)""",
            (name, email, course, phone)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_student.html")


# Edit student
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    if student is None:
        conn.close()
        return "Student not found!", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()
        phone = request.form["phone"].strip()

        if not all([name, email, course, phone]):
            conn.close()
            return "All fields are required!", 400

        conn.execute(
            """UPDATE students
            SET name=?, email=?, course=?, phone=?
            WHERE id=?""",
            (name, email, course, phone, id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_student.html", student=student)


# Delete student
@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
