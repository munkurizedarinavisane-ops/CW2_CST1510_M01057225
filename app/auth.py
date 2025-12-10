import bcrypt

# --- Password Hashing and Verification ---
def hash_password(plain_text_password: str) -> str:
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_text_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hash_bytes)

# --- Input Validation ---
def validate_username(username: str) -> tuple[bool, str]:
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters."
    if not username.isalnum():
        return False, "Username must be alphanumeric only."
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if len(password) > 50:
        return False, "Password too long (max 50 characters)."
    return True,""