from flask import Flask, request, jsonify
import sqlite3

web = Flask(__name__)

storage = "clean.db"


def build_database():

    link = sqlite3.connect(storage)

    pointer = link.cursor()

    pointer.execute("""
    CREATE TABLE IF NOT EXISTS members(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        secret TEXT
    )
    """)

    link.commit()

    link.close()


@web.route("/")
def index_page():

    return jsonify({
        "state": "ok"
    })


@web.route("/signup", methods=["POST"])
def signup():

    name = request.form.get("name", "").strip()

    secret = request.form.get("secret", "").strip()

    if len(name) < 3:

        return jsonify({
            "error": "invalid"
        }), 400

    if len(secret) < 8:

        return jsonify({
            "error": "invalid"
        }), 400

    link = sqlite3.connect(storage)

    pointer = link.cursor()

    pointer.execute(
        "INSERT INTO members(name, secret) VALUES(?, ?)",
        (name, secret)
    )

    link.commit()

    link.close()

    return jsonify({
        "message": "created"
    })


@web.route("/signin", methods=["POST"])
def signin():

    name = request.form.get("name", "").strip()

    secret = request.form.get("secret", "").strip()

    link = sqlite3.connect(storage)

    pointer = link.cursor()

    pointer.execute(
        "SELECT * FROM members WHERE name=? AND secret=?",
        (name, secret)
    )

    record = pointer.fetchone()

    link.close()

    if record:

        return jsonify({
            "message": "accepted"
        })

    return jsonify({
        "message": "denied"
    }), 401


if __name__ == "__main__":

    build_database()

    getattr(web, "run")()