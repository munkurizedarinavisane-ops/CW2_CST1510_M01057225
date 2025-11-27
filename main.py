import os
import hashlib
import secrets
import streamlit as st

USER_DATA_FILE = "users.txt"

# -------------------------
# Password Hashing Functions
# -------------------------
def hash_password(password, salt=None):
    """Hash a password with SHA-256 and a salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt

# -------------------------
# User Management Functions
# -------------------------
def user_exists(username):
    """Check if username exists in the file."""
    if not os.path.exists(USER_DATA_FILE):
        return False
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            stored_username = line.strip().split(":")[0]
            if stored_username == username:
                return True
    return False

def register_user(username, password):
    """Register a new user by saving username, salt, and hashed password."""
    if user_exists(username):
        return False, "Username already exists."
    hashed, salt = hash_password(password)
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username}:{salt}:{hashed}\n")
    return True, "Account created successfully!"

def login_user(username, password):
    """Check login credentials."""
    if not os.path.exists(USER_DATA_FILE):
        return False, "No user database found."
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_username, salt, stored_hash = line.strip().split(":")
            if stored_username == username:
                hashed_input, _ = hash_password(password, salt)
                if hashed_input == stored_hash:
                    return True, "Login successful! Welcome back."
                else:
                    return False, "Incorrect password."
    return False, "Username not found."

# -------------------------
# Validation Functions
# -------------------------
def validate_username(username):
    if len(username) < 7 or len(username) > 30:
        return False, "Username must be between 7 and 30 characters."
    if not username.isalnum():
        return False, "Username must contain only letters and numbers."
    return True, ""

def validate_password(password):
    if len(password) < 8 or len(password) > 70:
        return False, "Password must be between 8 and 70 characters."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    return True, ""

# -------------------------
# Streamlit App
# -------------------------
st.title("🔒 Smart Access Portal")
st.write("Secure Login & Registration System")

# Sidebar menu
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Register":
    st.header("Create a New Account")
    username = st.text_input("Choose a username", key="reg_user")
    password = st.text_input("Create a password", type="password", key="reg_pass")
    password_confirm = st.text_input("Confirm password", type="password", key="reg_pass_confirm")
    if st.button("Register"):
        is_valid, msg_user = validate_username(username)
        if not is_valid:
            st.error(msg_user)
        else:
            is_valid, msg_pass = validate_password(password)
            if not is_valid:
                st.error(msg_pass)
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(username, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

elif menu == "Login":
    st.header("Log In to Your Account")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Log In"):
        success, message = login_user(username, password)
        if success:
            st.success(message)
        else:
            st.error(message)
