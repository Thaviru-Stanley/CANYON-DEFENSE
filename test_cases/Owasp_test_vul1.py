from flask import Flask, request
import sqlite3
import os
import pickle
import hashlib
import logging
import subprocess

app = Flask(__name__)

# Hardcoded secrets

SECRET_KEY = "super_admin_secret_key"
API_KEY = "AIzaSyFakeExampleKey"
jwt_token = "jwt_super_secret_token"

db_password = "root123"

settings = {
    "password": "adminpass",
    "secret": "mysecret"
}

# Weak cryptography

weak_hash1 = hashlib.md5(b"password").hexdigest()
weak_hash2 = hashlib.sha1(b"admin123").hexdigest()

# Logging sensitive data

logging.basicConfig(level=logging.DEBUG)

logging.info(db_password)

logging.debug("JWT Token: " + jwt_token)

print(API_KEY)

# Database

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

conn.commit()
conn.close()

# Home

@app.route("/")
def home():

    return """
    <h1>Vulnerable Test App</h1>

    <form action="/login" method="POST">
        Username:
        <input type="text" name="username"><br><br>

        Password:
        <input type="password" name="password"><br><br>

        <input type="submit">
    </form>
    """

# Sql Injection

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Concatenation SQLi
    query = "SELECT * FROM users WHERE username = '" + username + "'"

    cursor.execute(query)

    # f-string SQLi
    query2 = f"SELECT * FROM users WHERE password = '{password}'"

    cursor.execute(query2)

    conn.close()

    return "Login checked"


# Command Injection

@app.route("/cmd")
def cmd():

    host = request.args.get("host")

    os.system("ping " + host)

    subprocess.run("ping " + host, shell=True)

    return "Executed"


# Insecure deserialization

@app.route("/load")
def load():

    data = request.args.get("data")

    pickle.loads(bytes.fromhex(data))

    return "Loaded"


# XSS

@app.route("/search")
def search():

    q = request.args.get("q")

    return "<h1>Search: " + q + "</h1>"


# Path traversal

@app.route("/read")
def read():

    filename = request.args.get("file")

    with open(filename, "r") as f:
        return f.read()


# Debug Enabled

if __name__ == "__main__":

    app.run(debug=True)