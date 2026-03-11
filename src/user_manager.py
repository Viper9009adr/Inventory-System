"""
User Manager - handles registration and login.

Passwords are NEVER stored in plain text.
werkzeug's generate_password_hash uses PBKDF2-SHA256 with a random salt.
Each password produces a different hash even if two users share the same password.
"""

from typing import Optional, Dict
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import DatabaseSession
from src.config import DB_NAME


def register_users(username: str, email: str, password: str, role: str) -> Dict:
    """
    Registers a new user.
    
    Hashes the password before storing.
    Raises ValueError on duplicate username or email.
    
    Returns:
        dict with user_id and username
    """
    if not username or not username.strip():
        raise ValueError("Username is required")
    if not email or not "@" in email:
        raise ValueError("valid email is required")
    if not password or len(password) < 8:
        raise ValueError("password must be atleast 8 characters.")
    # If role not explicitly provided, it falls back to a default value. It shouldn't never trigger this exception, nonetheless is a security measure.
    if not role or not role.strip():
        raise ValueError("role is required")
    
    hashed = generate_password_hash(password)

    try:
        with DatabaseSession(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                (username.strip(), email.strip().lower(), hashed, role.strip().lower())
            )
            return {
                "user_id" : cursor.lastrowid,
                "usarname" : username.strip(),
                "role": role.strip()
            }
    except Exception as e:
        # SQLite raises IntegrityError Unique constraint violation
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Username or password already exists.")
        raise


def login_user(username: str, password: str) -> Optional[Dict]:
    """
    Verifies credentials.
    
    Returns user dict if valid, None if not found or wrong password.
    Never reveals which fields was wrong nor leaks timing details.
    """
    username = username.strip() if username else ""
    password = password.strip() if password else ""
    
    with DatabaseSession(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, password FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()

    # always does hash lookup regardless of the previous outcome
    storedhash = row["password"] if row else "dummy"
    password_to_check = password if password else "empty"
    is_valid = check_password_hash(storedhash, password_to_check)

    if not username or not password or not row or not is_valid:
        return None
    
    return{
        "user_id": row["user_id"],
        "username": row["username"],
        "role": row["role"]
    }