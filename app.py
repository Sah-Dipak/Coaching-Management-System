from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DATABASE = "students.db"


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# DATABASE CREATE
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Students table
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        course TEXT NOT NULL,
        mobile TEXT NOT NULL
    )
    """)

    # Login history table
    c.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# HOME PAGE
@app.route('/')
def home():
    return render_template('login.html')


# LOGIN
@app.route('/login', methods=['POST'])
def login():

    user = request.form['username']
    password = request.form['password']
    role = request.form['role']

    conn = get_db_connection()
    c = conn.cursor()

    # ADMIN LOGIN
    if role == "admin":

        if user == "admin" and password == "1234":

            c.execute(
                "INSERT INTO logins (username, role) VALUES (?, ?)",
                (user, role)
            )

            conn.commit()
            conn.close()

            return redirect('/admin')

        else:
            conn.close()
            return "Invalid Admin Login"

    # STUDENT LOGIN
    elif role == "student":

        c.execute(
            "SELECT * FROM students WHERE name=?",
            (user,)
        )

        data = c.fetchone()

        if data:

            c.execute(
                "INSERT INTO logins (username, role) VALUES (?, ?)",
                (user, role)
            )

            conn.commit()
            conn.close()

            return redirect(f'/student/{user}')

        else:
            conn.close()
            return "Student Not Found"

    conn.close()
    return "Invalid Login"


# ADMIN DASHBOARD
@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html')


# STUDENT DASHBOARD
@app.route('/student/<name>')
def student(name):
    return render_template(
        'student_dashboard.html',
        name=name
    )


# REGISTER STUDENT
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        course = request.form['course']
        mobile = request.form['mobile']

        conn = get_db_connection()
        c = conn.cursor()

        c.execute("""
        INSERT INTO students (name, course, mobile)
        VALUES (?, ?, ?)
        """, (name, course, mobile))

        conn.commit()
        conn.close()

        return redirect('/students')

    return render_template('register.html')


# VIEW STUDENTS
@app.route('/students')
def students():

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM students")

    data = c.fetchall()

    conn.close()

    return render_template(
        'students.html',
        students=data
    )


# DELETE STUDENT
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/students')


# LOGIN HISTORY
@app.route('/logins')
def login_history():

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM logins
    ORDER BY time DESC
    """)

    data = c.fetchall()

    conn.close()

    return render_template(
        'logins.html',
        logins=data
    )


# TEST ROUTE
@app.route('/test')
def test():
    return render_template('admin_dashboard.html')


# CHECK TEMPLATE FILES
@app.route('/check')
def check():
    return str(os.listdir('templates'))


# MAIN
if __name__ == '__main__':

    init_db()   # IMPORTANT

    app.run(debug=True)