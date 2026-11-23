
import os
from dotenv import load_dotenv
from database import get_connection, _hash_password

load_dotenv(override=True)

email = os.getenv("ADMIN_EMAIL", "").strip().lower()
password = os.getenv("ADMIN_PASSWORD", "")
name = os.getenv("ADMIN_NAME", "Support Administrator")

if not email or not password:
    raise ValueError("ADMIN_EMAIL or ADMIN_PASSWORD is missing from .env")

if len(password) < 8:
    raise ValueError("Admin password must be at least 8 characters.")

password_hash = _hash_password(password)

with get_connection() as conn:
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()

    if existing:
        conn.execute(
            """
            UPDATE users
            SET name = ?, password_hash = ?, role = 'admin'
            WHERE email = ?
            """,
            (name, password_hash, email)
        )
        print("Existing administrator account updated.")
    else:
        conn.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, 'admin')
            """,
            (name, email, password_hash)
        )
        print("New administrator account created.")

print("Administrator credentials are ready.")
