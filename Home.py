# main.py
import os
import hashlib
import secrets
import bcrypt
import sqlite3
import streamlit as st
from pathlib import Path

# ============================================================
# CONFIG & FILE PATHS
# ============================================================
USER_DATA_FILE = "users.txt"
DB_FILE = "cyber.db"

# ============================================================
# DATABASE FUNCTIONS
# ============================================================
def connect_database():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()

def create_incidents_table():
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            severity TEXT,
            description TEXT,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ============================================================
# PASSWORD FUNCTIONS
# ============================================================
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Returns:
        str: The hashed password (safe to store in DB)
    """
    # Generate salt and hash
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Convert bytes to string for storing
    return hashed.decode('utf-8')


def hash_password_bcrypt(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def verify_password_bcrypt(password, hashed):
    if not hashed:
        return False
    # Strip whitespace/newlines
    hashed = hashed.strip()
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ============================================================
# LEGACY TEXT FILE AUTH FUNCTIONS
# ============================================================
def user_exists_txt(username):
    if not os.path.exists(USER_DATA_FILE):
        return False
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_username = line.strip().split(":", 1)[0]
            if stored_username == username:
                return True
    return False

def register_user_txt(username, password):
    if user_exists_txt(username):
        return False, "Username already exists in text file."
    hashed = hash_password_bcrypt(password)
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username}:{hashed}\n")
    return True, "Account created successfully in text file."

def login_user_txt(username, password):
    if not os.path.exists(USER_DATA_FILE):
        return False, "No text-file users found."
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_username, stored_hash = line.strip().split(":", 1)
            if stored_username == username:
                if verify_password_bcrypt(password, stored_hash):
                    return True, "Login successful (text file)."
                else:
                    return False, "Incorrect password."
    return False, "Username not found."

# ============================================================
# DATABASE AUTH FUNCTIONS
# ============================================================
def user_exists_db(username):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def register_user_db(username, password):
    if user_exists_db(username):
        return False, "Username already exists in database."
    hashed = hash_password_bcrypt(password)
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()
    return True, "Account created successfully in database."

def login_user_db(username, password):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return False, "Username not found in database."
    if verify_password_bcrypt(password, user["password_hash"]):
        return True, "Login successful (database)."
    else:
        return False, "Incorrect password."

# ============================================================
# VALIDATION FUNCTIONS
# ============================================================
def validate_username(username):
    if len(username) < 7 or len(username) > 30:
        return False, "Username must be 7-30 chars."
    if not username.isalnum():
        return False, "Username must be letters & numbers only."
    return True, ""

def validate_password(password):
    if len(password) < 8 or len(password) > 70:
        return False, "Password must be 8-70 chars."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain a digit."
    if not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter."
    if not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter."
    return True, ""

# ============================================================
# LEGACY MIGRATION
# ============================================================
def migrate_users_to_db():
    """
    Migrate legacy text-file users to the database safely.
    Skips users with invalid bcrypt hashes.
    """
    if not os.path.exists(USER_DATA_FILE):
        return

    create_users_table()
    conn = connect_database()
    cursor = conn.cursor()
    migrated = 0
    skipped = []

    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                username, hashed = line.split(":", 1)
            except ValueError:
                # Malformed line, skip
                continue

            # Clean hash whitespace
            hashed_clean = "".join(hashed.split())

            # Check if the hash is valid bcrypt
            try:
                bcrypt.checkpw(b"test", hashed_clean.encode())
            except ValueError:
                skipped.append(username)
                continue

            if not user_exists_db(username):
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hashed_clean)
                )
                migrated += 1

    conn.commit()
    conn.close()

    if migrated > 0:
        st.success(f"Migrated {migrated} legacy user(s) to database.")
    if skipped:
        st.warning(f"Skipped {len(skipped)} user(s) with invalid hashes: {', '.join(skipped)}")

# ============================================================
# STREAMLIT APP
# ============================================================
st.set_page_config(page_title="🔒 Smart Access Portal", layout="wide")
st.title("🔒 Smart Access Portal")

# Run migration once at startup
migrate_users_to_db()
create_incidents_table()

# --- Sidebar Menu ---
auth_mode = st.sidebar.selectbox("Authentication Mode", ["Database", "Legacy (Text File)"])
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Register":
    st.header("Create New Account")
    username = st.text_input("Username", key="reg_user")
    password = st.text_input("Password", type="password", key="reg_pass")
    password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
    if st.button("Register"):
        valid, msg = validate_username(username)
        if not valid:
            st.error(msg)
        else:
            valid, msg = validate_password(password)
            if not valid:
                st.error(msg)
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                if auth_mode == "Database":
                    success, message = register_user_db(username, password)
                else:
                    success, message = register_user_txt(username, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

elif menu == "Login":
    st.header("Log In")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Log In"):
        if auth_mode == "Database":
            success, message = login_user_db(username, password)
        else:
            success, message = login_user_txt(username, password)
        if success:
            st.success(message)
            st.session_state["user"] = {"username": username}
        else:
            st.error(message)

# ============================================================
# MODULE NAVIGATION
# ============================================================
if st.session_state.get("user"):
    st.sidebar.header(f"Welcome, {st.session_state['user']['username']}")
    import modules.cyber_incidents as ci
    ci.run()
