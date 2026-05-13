from flask import Flask, request, jsonify, session
import sqlite3
import hashlib
import secrets
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


# Secure Configuration

app.secret_key = secrets.token_hex(32)

DATABASE = "secure_users.db"


# Database Setup

def init_db():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Secure password hashing
    hashed_password = generate_password_hash("SecureAdmin123!")

    cursor.execute("""
    INSERT OR IGNORE INTO users(username,password,role)
    VALUES(?,?,?)
    """, ("admin", hashed_password, "admin"))

    conn.commit()
    conn.close()


# ======================================================
# HOME
# ======================================================
@app.route("/")
def home():

    return """
    <h1>Secure OWASP Flask Application</h1>

    <ul>
        <li>/register</li>
        <li>/login</li>
        <li>/search?q=test</li>
        <li>/profile</li>
    </ul>
    """


# ======================================================
# SECURE USER REGISTRATION
# ======================================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return "Username and password required"

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:

            # Parameterized query prevents SQL Injection
            cursor.execute("""
            INSERT INTO users(username,password,role)
            VALUES(?,?,?)
            """, (username, hashed_password, "user"))

            conn.commit()

        except sqlite3.IntegrityError:
            return "User already exists"

        finally:
            conn.close()

        return "Registration successful"

    return """
    <h2>Register</h2>

    <form method='POST'>
        Username: <input name='username'><br><br>
        Password: <input type='password' name='password'><br><br>
        <input type='submit'>
    </form>
    """


# ======================================================
# SECURE LOGIN
# ======================================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Secure parameterized query
        cursor.execute(
            "SELECT username, password, role FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[1], password):

            session["user"] = user[0]
            session["role"] = user[2]

            return f"Welcome {user[0]}"

        return "Invalid credentials"

    return """
    <h2>Login</h2>

    <form method='POST'>
        Username: <input name='username'><br><br>
        Password: <input type='password' name='password'><br><br>
        <input type='submit'>
    </form>
    """


# ======================================================
# SECURE SEARCH
# ======================================================
@app.route("/search")
def search():

    query = request.args.get("q", "").strip()

    # Flask automatically escapes HTML here
    return jsonify({
        "search_term": query,
        "status": "safe"
    })


# ======================================================
# SECURE PROFILE ACCESS
# ======================================================
@app.route("/profile")
def profile():

    if "user" not in session:
        return "Unauthorized", 401

    return jsonify({
        "username": session["user"],
        "role": session["role"]
    })


# ======================================================
# SECURE HASHING EXAMPLE
# ======================================================
@app.route("/hash")
def secure_hash():

    text = request.args.get("text", "")

    # SHA-256 instead of weak MD5
    secure_digest = hashlib.sha256(text.encode()).hexdigest()

    return {
        "sha256": secure_digest
    }


# ======================================================
# SECURE ERROR HANDLING
# ======================================================
@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error": "Resource not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):

    return jsonify({
        "error": "Internal server error"
    }), 500


# ======================================================
# APPLICATION START
# ======================================================
if __name__ == "__main__":

    init_db()

    # Debug disabled in production
    app.run(debug=False)