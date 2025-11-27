# auth.py
# Simple CLI helpers for user registration/login using bcrypt and users.txt

import bcrypt
import getpass
from pathlib import Path
import sqlite3

USERS_TXT = Path("users.txt")


def hash_password(plain_password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt)


def verify_password(plain_password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed)


def register_cli():
    username = input("Choose username: ")
    if not username:
        print("Username required")
        return

    password = getpass.getpass("Choose password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match")
        return

    # Load existing users
    users = {}
    if USERS_TXT.exists():
        with USERS_TXT.open("rb") as f:
            for line in f:
                try:
                    user, hashed = line.strip().split(b":", 1)
                    users[user.decode()] = hashed
                except Exception:
                    continue

    if username in users:
        print("Username already exists")
        return

    hashed = hash_password(password)

    # Append new user
    with USERS_TXT.open("ab") as f:
        f.write(username.encode() + b":" + hashed + b"\n")

    print("Registered successfully")


def login_cli():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    if not USERS_TXT.exists():
        print("No users registered yet.")
        return False

    with USERS_TXT.open("rb") as f:
        for line in f:
            try:
                user, hashed = line.strip().split(b":", 1)
                if user.decode() == username:
                    if verify_password(password, hashed):
                        print("Login success")
                        return True
                    else:
                        print("Invalid password")
                        return False
            except Exception:
                continue

    print("User not found")
    return False


if __name__ == "__main__":
    print("Auth CLI — choose: [r]egister, [l]ogin")
    c = input("> ").strip().lower()

    if c == "r":
        register_cli()
    elif c == "l":
        login_cli()
    else:
        print("Bye")
