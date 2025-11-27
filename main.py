import os
import hashlib
import secrets

USER_DATA_FILE = "users.txt"


def hash_password(password, salt=None):
    """
    Hashes a password with SHA-256 and a randomly generated salt.
    Salt is returned so it can be stored for later password verification.
    """
    if salt is None:
        salt = secrets.token_hex(16)

    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt


def register_user(username, password):
    """
    Saves a new user to the file in a secure hashed format.
    Format stored:
    username:salt:hashed_password
    """
    # Check if username exists
    if user_exists(username):
        print(" Username already exists. Please choose another one.")
        return

    hashed, salt = hash_password(password)

    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username}:{salt}:{hashed}\n")

    print(" Account created successfully!")


def login_user(username, password):
    """
    Validates login by comparing stored username/password hash.
    """
    if not os.path.exists(USER_DATA_FILE):
        print(" No user database found. No accounts exist yet.")
        return False

    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_username, salt, stored_hash = line.strip().split(":")

            if stored_username == username:
                # Recompute hash with the same salt
                hashed_input, _ = hash_password(password, salt)

                if hashed_input == stored_hash:
                    print(" Login successful! Welcome back.")
                    return True
                else:
                    print(" Incorrect password.")
                    return False

    print(" Username not found.")
    return False

# MENU INTERFACE
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
            print("\n Create a New Account")
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