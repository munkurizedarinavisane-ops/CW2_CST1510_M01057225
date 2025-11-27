import os
import bcrypt

from app.db import connect_database

from app.schema import create_users_table
from app.users import get_user_by_username, insert_user

# This file stores users for the legacy text-based system.
# It's used for compatibility and migration to the database.
USER_DATA_FILE = "user.txt"



#  PASSWORD SECURITY


def hash_password(plain_text_password):
    """
    Hashes a plain text password using bcrypt.
    - Adds a salt automatically.
    - Returns the hashed password as a UTF-8 string.
    """
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    """
    Checks if a plain text password matches a stored bcrypt hash.
    Returns True if the password is correct, False otherwise.
    """
    password_bytes = plain_text_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

# ============================================================
#  DATABASE-BASED LOGIN FOR STREAMLIT (WEEK 9)
# ============================================================

def authenticate_user(username, password):
    """
    Authenticates a user using the SQLite database (Week 8+9 login system).
    Returns a dict with username + role if valid, otherwise None.
    """

    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()

    except Exception as e:
        print("Database error:", e)
        conn.close()
        return None

    conn.close()

    if not user:
        return None  # username does not exist

    stored_hash = user["password_hash"]

    # Validate password using bcrypt
    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return {"username": user["username"], "role": user["role"]}

    return None

#  USER MANAGEMENT (LEGACY FILE-BASED SYSTEM)


def user_exists(username):
    """
    Checks if a username already exists in the text file.
    Returns True if found, False otherwise.
    """
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            stored_username = line.strip().split(":")[0]
            if stored_username == username:
                return True
    return False


def register_user(username, password):
    """
    Registers a new user.
    - Validates that the username isn't taken.
    - Hashes the password before saving.
    """
    if user_exists(username):
        print(f"  The username '{username}' is already in use. Please try a different one.")
        return False

    hashed_pw = hash_password(password)
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username}:{hashed_pw}\n")

    print(f" Account '{username}' created successfully! You can now log in.")
    return True


def login_user(username, password):
    """
    Logs a user in by checking credentials in the text file.
    Returns True if login succeeds, False if not.
    """
    if not os.path.exists(USER_DATA_FILE):
        print("⚠️  No accounts found. Please register first.")
        return False

    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            stored_username, stored_hashed = line.strip().split(":")
            if stored_username == username:
                if verify_password(password, stored_hashed):
                    print(f" Welcome back, {username}! You’re now logged in.")
                    return True
                else:
                    print(" Incorrect password. Please try again.")
                    return False

    print(" No account found with that username. Please check your entry or sign up.")
    return False



#  INPUT VALIDATION


def validate_username(username):
    """
    Ensures a username meets the following rules:
    - Between 7 and 30 characters.
    - Contains only letters and numbers.
    """
    if len(username) < 7 or len(username) > 30:
        return False, "Username must be between 7 and 30 characters long."
    if not username.isalnum():
        return False, "Username must contain only letters and numbers."
    return True, ""


def validate_password(password):
    """
    Ensures a password meets these security rules:
    - Between 8 and 70 characters.
    - Includes at least one digit, one lowercase, and one uppercase letter.
    """
    if len(password) < 8 or len(password) > 70:
        return False, "Password must be between 8 and 70 characters long."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    return True, ""



#  MIGRATION TOOL (FROM TEXT FILE TO DATABASE)


def migrate_users_from_file(filepath='DATA/users.txt'):
    """
    Moves existing users from a legacy text file into the database.
    - Skips users who already exist in the database.
    - Creates the users table if it doesn’t exist.
    """
    conn = connect_database()
    create_users_table(conn)

    if not os.path.exists(filepath):
        print(f"  File '{filepath}' not found. Skipping migration.")
        return

    migrated_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue  # skip lines that aren’t properly formatted

            username, hashed_pw = line.split(":", 1)

            # Skip if user is already in the database
            if get_user_by_username(conn, username):
                print(f" Skipping existing user: {username}")
                continue

            # Insert the migrated user
            insert_user(conn, username, hashed_pw)
            migrated_count += 1
            print(f" Migrated user: {username}")

    conn.close()
    print(f"\n Migration complete! {migrated_count} user(s) migrated successfully.")



#  MENU INTERFACE


def display_menu():
    """
    Displays the main options for the user.
    """
    print("\n" + "="*50)
    print("  Welcome to the Smart Access Portal")
    print("  Secure Login & Registration System")
    print("="*50)
    print("\n[1] Create a new account")
    print("[2] Log in to your account")
    print("[3] Exit")
    print("-"*50)


def main():
    """
    Main program loop:
    - Lets users register, log in, or exit.
    - Repeats until the user chooses to quit.
    """
    print("\n Welcome to the Week 7 Authentication System! ")
    print("Your secure and easy-to-use login platform.\n")

    while True:
        display_menu()
        choice = input("\nSelect an option (1-3): ").strip()

        if choice == '1':
            # --- User Registration ---
            print("\n🆕 Create a New Account")
            username = input("Choose a username: ").strip()

            # Check username validity
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f" {error_msg}")
                continue

            password = input("Create a password: ").strip()

            # Check password strength
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f" {error_msg}")
                continue

            password_confirm = input("Confirm your password: ").strip()
            if password != password_confirm:
                print(" Passwords don’t match. Please try again.")
                continue

            register_user(username, password)

        elif choice == '2':
            # --- User Login ---
            print("\n Log In to Your Account")
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            login_user(username, password)
            input("\nPress Enter to return to the main menu...")

        elif choice == '3':
            print("\n Thank you for using the authentication system!")
            print("Have a great day! Exiting now...")
            break

        else:
            print("\n Invalid choice. Please enter 1, 2, or 3.")


# ============================================================
#  PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Optional: migrate legacy users automatically when the program starts
    # migrate_users_from_file(filepath=USER_DATA_FILE)

    main()
