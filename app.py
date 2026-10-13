#!/usr/bin/python
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# DATABASE FUNCTIONS

def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn


def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)
        conn.commit()
        print("User table created successfully")
    finally:
        conn.close()


# CREATE: INSERT A USER

def insert_user(user):
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users
                (name, email, phone, address, country)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user["name"],
            user["email"],
            user["phone"],
            user["address"],
            user["country"]
        ))

        conn.commit()
        user_id = cur.lastrowid
        return get_user_by_id(user_id)

    finally:
        conn.close()


# READ: GET ALL USERS

def get_users():
    conn = connect_to_db()

    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM users"
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# READ: GET ONE USER

def get_user_by_id(user_id):
    conn = connect_to_db()

    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        return dict(row) if row else {}

    finally:
        conn.close()


# UPDATE: MODIFY A USER

def update_user(user):
    conn = connect_to_db()

    try:
        conn.execute("""
            UPDATE users
            SET name = ?, email = ?, phone = ?,
                address = ?, country = ?
            WHERE user_id = ?
        """, (
            user["name"],
            user["email"],
            user["phone"],
            user["address"],
            user["country"],
            user["user_id"]
        ))

        conn.commit()
        return get_user_by_id(user["user_id"])

    finally:
        conn.close()


# DELETE: REMOVE A USER

def delete_user(user_id):
    conn = connect_to_db()

    try:
        cur = conn.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()

        if cur.rowcount > 0:
            return {"status": "User deleted successfully"}

        return {"status": "User not found"}

    finally:
        conn.close()


# REST API ENDPOINTS

@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users())


@app.route("/api/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))


@app.route("/api/users/add", methods=["POST"])
def api_add_user():
    user = request.get_json()
    return jsonify(insert_user(user))


@app.route("/api/users/update", methods=["PUT"])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))


@app.route("/api/users/delete/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))


if __name__ == "__main__":
    create_db_table()
    app.run(debug=True)
