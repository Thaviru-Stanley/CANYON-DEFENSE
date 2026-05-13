from flask import Flask, request, render_template_string
import sqlite3
import os
import subprocess
import pickle

app = Flask(__name__)
app.secret_key = "hardcoded-secret-key"  # OWASP: Sensitive Data Exposure

DATABASE = "users.db"

# Create Database

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    # Default admin account
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")

    conn.commit()
    conn.close()


# Home page
@app.route('/')
def home():
    return '''
    <h1>OWASP Vulnerable Python Application</h1>

    <ul>
        <li><a href='/login'>Login</a></li>
        <li><a href='/search'>Search</a></li>
        <li><a href='/ping'>Ping Host</a></li>
        <li><a href='/profile?name=test'>Profile</a></li>
        <li><a href='/load'>Unsafe Deserialization</a></li>
    </ul>
    '''


# SQL Injection
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # OWASP: SQL Injection Vulnerability
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        print("Executing Query:", query)

        cursor.execute(query)
        user = cursor.fetchone()

        conn.close()

        if user:
            return f"<h2>Welcome {username}</h2>"
        else:
            return "<h2>Invalid credentials</h2>"

    return '''
    <h2>Login</h2>
    <form method='POST'>
        Username: <input type='text' name='username'><br><br>
        Password: <input type='password' name='password'><br><br>
        <input type='submit' value='Login'>
    </form>
    '''


# Cross site scripting (XSS)
@app.route('/search')
def search():
    keyword = request.args.get('q', '')

    # OWASP: Reflected XSS
    return f'''
    <h2>Search Results</h2>
    You searched for: {keyword}
    '''


# Command Injection
@app.route('/ping')
def ping():
    host = request.args.get('host', '')

    # OWASP: Command Injection
    command = f"ping -c 1 {host}"

    result = os.popen(command).read()

    return f'''
    <h2>Ping Result</h2>
    <pre>{result}</pre>
    '''


# Path traversal
@app.route('/read')
def read_file():
    filename = request.args.get('file', '')

    # OWASP: Path Traversal
    try:
        with open(filename, 'r') as f:
            content = f.read()

        return f"<pre>{content}</pre>"

    except Exception as e:
        return str(e)


# Insecure Deserialization
@app.route('/load')
def load_data():
    filename = request.args.get('file', 'data.pkl')

    try:
        with open(filename, 'rb') as f:

            # OWASP: Unsafe Deserialization
            data = pickle.load(f)

        return f"Loaded Data: {data}"

    except Exception as e:
        return str(e)


# Hardcoded Credentials + Information Disclosure

@app.route('/config')
def config():
    return {
        "database": DATABASE,
        "secret_key": app.secret_key,
        "admin_password": "admin123"
    }


# Broken Access Control
@app.route('/admin')
def admin_panel():
    # No authentication check
    return '''
    <h1>Admin Panel</h1>
    <p>All user information visible.</p>
    '''


# Debug Mode Enabled
if __name__ == '__main__':
    init_db()

    # OWASP: Security Misconfiguration
    app.run(debug=True)
