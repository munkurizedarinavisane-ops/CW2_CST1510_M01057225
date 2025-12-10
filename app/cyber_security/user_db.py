import sqlite3
import os
from app.auth import hash_password, verify_password, validate_username, validate_password

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "data", "USER_DATABASE.db")

# Ensure the data folder exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# --- DB Connection ---
def connect_db():
    return sqlite3.connect(DB_FILE)

# --- Users Table ---
def create_users_table():
    """Creates the users table if it doesn't exist."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ensure table exists on import
create_users_table()

# --- Register User ---
def register_user(username: str, password: str) -> dict:
    ok, msg = validate_username(username)
    if not ok:
        return {"success": False, "message": msg}

    ok, msg = validate_password(password)
    if not ok:
        return {"success": False, "message": msg}

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        return {"success": False, "message": "Username entered already exists."}

    hashed = hash_password(password)
    cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

    return {"success": True, "message": "User registered successfully."}

# --- Authenticate User ---
def authenticate_user(username: str, password: str) -> bool:
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    stored_hash = row[0]
    return verify_password(password, stored_hash)

# --- Helper to get DB path ---
def getDBPath():
    return DB_FILE
