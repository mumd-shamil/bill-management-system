"""
auth_db.py
Handles user authentication: creating users and verifying logins.
Passwords are stored as SHA-256 hashes (never in plain text).
"""

import hashlib
from database import get_connection


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username: str, password: str, role: str) -> tuple[bool, str]:
    """Create a new user. Returns (success, message)."""
    if not username or not password:
        return False, "Username and password cannot be empty."
    if role not in ("admin", "cashier"):
        return False, "Role must be 'admin' or 'cashier'."

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )
        conn.commit()
        return True, "User created successfully."
    except Exception as e:
        if "UNIQUE" in str(e):
            return False, "Username already exists."
        return False, f"Error creating user: {e}"
    finally:
        conn.close()


def verify_login(username: str, password: str):
    """Return (user_id, role) if credentials are valid, else None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    user_id, stored_hash, role = row
    if hash_password(password) == stored_hash:
        return (user_id, role)
    return None


def ensure_default_admin():
    """Create a default admin account on first run if no users exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()

    if count == 0:
        create_user("admin", "admin123", "admin")
        create_user("cashier", "cashier123", "cashier")
