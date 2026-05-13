from flask import Flask, request, session, render_template_string
import sqlite3
import subprocess
import json
import hashlib
import os
import urllib.request

app = Flask(__name__)
app.secret_key = "temporary-dev-key"

DATABASE = "portal.db"

# Database Setuo
def setup_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO accounts(username,password,role)
    VALUES('admin','password123','admin')
    """)

    conn.commit()
    conn.close()


# Home
@app.route("/")
def home():
    return """
    <h1>Employee Portal</h1>

    <ul>
        <li>/signin</li>
        <li>/lookup?name=test</li>
        <li>/tools?host=127.0.0.1</li>
        <li>/viewer?doc=notes.txt</li>
        <li>/profile</li>
    </ul>
    """

# SQL Injection
@app.route("/signin", methods=["GET", "POST"])
def signin():

    if request.method == "POST":

        user = request.form.get("username", "")
        pw = request.form.get("password", "")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        conditions = []
        conditions.append(f"username='{user}'")
        conditions.append(f"password='{pw}'")

        sql = "SELECT * FROM accounts WHERE " + " AND ".join(conditions)

        result = cursor.execute(sql).fetchone()

        conn.close()

        if result:
            session["user"] = user
            return f"Welcome {user}"

        return "Login failed"

    return """
    <h2>Sign In</h2>

    <form method='POST'>
        Username: <input name='username'><br><br>
        Password: <input type='password' name='password'><br><br>
        <input type='submit'>
    </form>
    """


# Indirect XSS
@app.route("/lookup")
def lookup():

    name = request.args.get("name", "")

    template = """
    <h2>Directory Search</h2>
    <p>User searched for:</p>
    <div>%s</div>
    """ % name

    return render_template_string(template)


# Subprocess Misuse
@app.route("/tools")
def tools():

    host = request.args.get("host", "localhost")

    cmd_parts = ["ping", "-c", "1", host]

    result = subprocess.getoutput(" ".join(cmd_parts))

    return f"<pre>{result}</pre>"


# File Access Issue
@app.route("/viewer")
def viewer():

    doc = request.args.get("doc", "readme.txt")

    path = os.path.join("documents", doc)

    try:
        with open(path, "r") as file:
            return f"<pre>{file.read()}</pre>"

    except Exception as e:
        return str(e)


# Weak Token Generation
@app.route("/token")
def token():

    user = request.args.get("user", "guest")

    token = hashlib.md5(user.encode()).hexdigest()

    return {"token": token}


# SSRF-like URL fetch
@app.route("/proxy")
def proxy():

    target = request.args.get("url")

    if not target:
        return "Missing URL"

    response = urllib.request.urlopen(target)

    return response.read()


# Excessive information Disclosure
@app.route("/profile")
def profile():

    return {
        "application": "Employee Portal",
        "environment": dict(os.environ),
        "debug": True,
        "secret_key": app.secret_key
    }


# Debug Enabled
if __name__ == "__main__":

    setup_database()

    app.run(debug=True)