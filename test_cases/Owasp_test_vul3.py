from flask import Flask, request, jsonify, render_template_string
import sqlite3
import hashlib
import os
import base64
import yaml
import requests

app = Flask(__name__)

SECRET_KEY = "super-secret-admin-key"
API_TOKEN = "123456789-SECRET-TOKEN"

DB_NAME = "employees.db"


# Database setup
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute(
        "INSERT INTO employees(username,password,role) VALUES('admin','admin123','administrator')"
    )

    conn.commit()
    conn.close()


# Home
@app.route('/')
def home():
    return """
    <h1>OWASP Vulnerable Application 2</h1>

    <ul>
        <li>/login</li>
        <li>/search?q=test</li>
        <li>/download?file=test.txt</li>
        <li>/exec?cmd=whoami</li>
        <li>/deserialize</li>
        <li>/config</li>
        <li>/fetch?url=http://example.com</li>
    </ul>
    """


# SQL Injection
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Vulnerable SQL query
        query = f"SELECT * FROM employees WHERE username='{username}' AND password='{password}'"

        print("Executing:", query)

        cursor.execute(query)

        result = cursor.fetchone()

        conn.close()

        if result:
            return f"Welcome {username}"
        else:
            return "Invalid login"

    return """
    <h2>Login</h2>

    <form method='POST'>
        Username: <input type='text' name='username'><br><br>
        Password: <input type='password' name='password'><br><br>
        <input type='submit'>
    </form>
    """


# XSS
@app.route('/search')
def search():
    q = request.args.get('q', '')

    html = f"""
    <h2>Search Results</h2>
    Results for: {q}
    """

    return render_template_string(html)


# Command Injection
@app.route('/exec')
def execute_command():
    cmd = request.args.get('cmd')

    output = os.popen(cmd).read()

    return f"<pre>{output}</pre>"


# Path Traversal
@app.route('/download')
def download_file():

    filename = request.args.get('file')

    with open(filename, 'r') as f:
        data = f.read()

    return f"<pre>{data}</pre>"


# Weak Password Hashing
@app.route('/hash')
def weak_hash():

    password = request.args.get('password', '')

    # Weak MD5 hashing
    hashed = hashlib.md5(password.encode()).hexdigest()

    return f"MD5 Hash: {hashed}"


# Insecure Desrialization
@app.route('/deserialize', methods=['POST'])
def deserialize_data():

    user_input = request.data

    # Unsafe YAML deserialization
    data = yaml.load(user_input, Loader=yaml.Loader)

    return jsonify({"data": str(data)})


# Sensitive data expoture
@app.route('/config')
def config():
    return jsonify({
        "secret_key": SECRET_KEY,
        "api_token": API_TOKEN,
        "database": DB_NAME
    })


# Serser Side Request Forgery
@app.route('/fetch')
def fetch_url():

    url = request.args.get('url')

    response = requests.get(url)

    return response.text


# Broken Access Control
@app.route('/admin')
def admin():

    # No authentication
    return """
    <h1>Admin Dashboard</h1>
    <p>Confidential employee records available.</p>
    """


# Information Disclosure
@app.route('/debug')
def debug():

    return {
        "environment": dict(os.environ)
    }


# Application Start
if __name__ == '__main__':

    init_db()

    # Security Misconfiguration
    app.run(debug=True)