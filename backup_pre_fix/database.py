import os
import re
import hmac
import hashlib
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_PATH = Path(__file__).parent / "support_tickets.db"
PBKDF2_ITERATIONS = 310_000


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    ).hex()
    return f"{salt}${digest}"


def _verify_password(password, stored):
    try:
        salt, expected = stored.split("$", 1)
    except (AttributeError, ValueError):
        return False
    actual = _hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(actual, expected)


def _provision_admin():
    name = os.getenv("ADMIN_NAME", "Support Administrator").strip()
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")
    # Admin creation is disabled until all credentials are configured.
    if not email or not password:
        return
    if len(password) < 8:
        raise ValueError("ADMIN_PASSWORD must be at least 8 characters.")
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return
        conn.execute(
            "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin')",
            (name or "Support Administrator", email, _hash_password(password)),
        )


def _sla_due_datetime(result):
    """Return a local ISO timestamp based on the ticket's configured SLA target."""
    import re
    from datetime import timedelta

    label = str((result or {}).get("sla_target") or "8 hours").lower()
    hours_match = re.search(r"(\\d+(?:\\.\\d+)?)\\s*hours?", label)
    minutes_match = re.search(r"(\\d+(?:\\.\\d+)?)\\s*minutes?", label)

    if hours_match:
        duration = timedelta(hours=float(hours_match.group(1)))
    elif minutes_match:
        duration = timedelta(minutes=float(minutes_match.group(1)))
    elif "immediate" in label:
        # Operational reporting target for an immediate-review queue.
        duration = timedelta(minutes=30)
    else:
        duration = timedelta(hours=8)

    return (datetime.now() + duration).isoformat(timespec="seconds")


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_text TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'General Inquiry',
                urgency TEXT NOT NULL DEFAULT 'Medium',
                sentiment TEXT NOT NULL DEFAULT 'Neutral',
                summary TEXT NOT NULL DEFAULT '',
                draft_reply TEXT NOT NULL DEFAULT '',
                escalate INTEGER NOT NULL DEFAULT 0,
                escalation_reason TEXT,
                approval_status TEXT NOT NULL DEFAULT 'Pending',
                assigned_team TEXT NOT NULL DEFAULT 'General Support',
                escalation_status TEXT NOT NULL DEFAULT 'Normal',
                rule_triggered TEXT DEFAULT 'Standard Routing',
                sla_target TEXT DEFAULT '8 hours',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        current = {row["name"] for row in conn.execute("PRAGMA table_info(tickets)").fetchall()}
        additions = {
            "user_id": "INTEGER REFERENCES users(id)",
            "subject": "TEXT DEFAULT 'Support request'",
            "ticket_status": "TEXT NOT NULL DEFAULT 'Open'",
            "analysis_mode": "TEXT NOT NULL DEFAULT 'Rule-Based Fallback'",
            "model_used": "TEXT",
            "updated_at": "TEXT",

            "station_id": "TEXT",
            "station_name": "TEXT",
            "station_city": "TEXT",
            "transaction_id": "TEXT",
            "session_id": "TEXT",
            "vehicle_model": "TEXT",
            "sla_due_at": "TEXT",
            "resolved_at": "TEXT",
        }
        for column, definition in additions.items():
            if column not in current:
                conn.execute(f"ALTER TABLE tickets ADD COLUMN {column} {definition}")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)")
        # Backfill SLA deadlines for pre-existing tickets without changing their status.
        legacy_rows = conn.execute(
            "SELECT id, sla_target FROM tickets WHERE sla_due_at IS NULL"
        ).fetchall()
        for legacy in legacy_rows:
            due_at = _sla_due_datetime({"sla_target": legacy["sla_target"]})
            conn.execute(
                "UPDATE tickets SET sla_due_at=? WHERE id=?",
                (due_at, legacy["id"]),
            )
    _provision_admin()


def create_user(name, email, password, role="user"):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    if not name:
        raise ValueError("Please enter your full name.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Please enter a valid email address.")
    if len(password or "") < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if role != "user":
        raise ValueError("Public registration is only available for customer accounts.")
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'user')",
                (name, email, _hash_password(password)),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("An account with this email already exists.") from None


def authenticate_user(email, password):
    email = (email or "").strip().lower()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id,name,email,password_hash,role FROM users WHERE email = ?", (email,)
        ).fetchone()
    if not row or not _verify_password(password or "", row["password_hash"]):
        return None
    return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}



def save_ticket(
    ticket_text,
    result,
    user_id=None,
    subject="Support request",
    station_id=None,
    station_name=None,
    station_city=None,
    transaction_id=None,
    session_id=None,
    vehicle_model=None,
):
    required = (
        "category", "urgency", "sentiment",
        "summary", "draft_reply"
    )

    missing = [field for field in required if field not in result]

    if missing:
        raise ValueError("Analysis missing: " + ", ".join(missing))

    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO tickets (
                ticket_text, category, urgency, sentiment,
                summary, draft_reply, escalate, escalation_reason,
                approval_status, assigned_team, escalation_status,
                rule_triggered, sla_target, user_id, subject,
                ticket_status, analysis_mode, model_used, updated_at,
                station_id, station_name, station_city,
                transaction_id, session_id, vehicle_model
            )
            VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                'Open',?,?,?,
                ?,?,?,?,?,?
            )
        """, (
            ticket_text,
            result["category"],
            result["urgency"],
            result["sentiment"],
            result["summary"],
            result["draft_reply"],
            int(bool(result.get("escalate", False))),
            result.get("escalation_reason"),
            "Pending",
            result.get("assigned_team", "General Support"),
            result.get("escalation_status", "Normal"),
            result.get("rule_triggered", "Standard Routing"),
            result.get("sla_target", "8 hours"),
            user_id,
            (subject or "Support request").strip(),
            result.get("analysis_mode", "Rule-Based Fallback"),
            result.get("model_used"),
            datetime.now().isoformat(timespec="seconds"),
            station_id,
            station_name,
            station_city,
            transaction_id,
            session_id,
            vehicle_model,
        ))

        ticket_id = cur.lastrowid
        created_at = datetime.now().isoformat(timespec="seconds")
        sla_due_at = _sla_due_datetime(result)
        conn.execute(
            "UPDATE tickets SET created_at=?, sla_due_at=? WHERE id=?",
            (created_at, sla_due_at, ticket_id),
        )
        return ticket_id



def get_all_tickets():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT t.*, u.name AS customer_name, u.email AS customer_email
            FROM tickets t LEFT JOIN users u ON u.id=t.user_id
            ORDER BY t.id DESC
        """).fetchall()
        return [dict(row) for row in rows]


def get_user_tickets(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets WHERE user_id=? ORDER BY id DESC", (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_ticket(ticket_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
        return dict(row) if row else None


def update_approval_status(ticket_id, status):
    if status not in {"Pending", "Approved", "Rejected"}:
        raise ValueError("Invalid approval status.")
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE tickets SET approval_status=?, updated_at=? WHERE id=?",
            (status, datetime.now().isoformat(timespec="seconds"), ticket_id),
        )
        if cur.rowcount == 0:
            raise ValueError("Ticket not found.")


def update_ticket_reply(ticket_id, draft_reply):
    draft_reply = (draft_reply or "").strip()
    if not draft_reply:
        raise ValueError("Reply cannot be empty.")
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE tickets SET draft_reply=?, updated_at=? WHERE id=?",
            (draft_reply, datetime.now().isoformat(timespec="seconds"), ticket_id),
        )
        if cur.rowcount == 0:
            raise ValueError("Ticket not found.")


def update_ticket_status(ticket_id, status, assigned_team=None):
    if status not in {"Open", "In Progress", "Resolved", "Closed"}:
        raise ValueError("Invalid ticket status.")
    with get_connection() as conn:
        now = datetime.now().isoformat(timespec="seconds")
        resolved_at = now if status in {"Resolved", "Closed"} else None
        if assigned_team:
            cur = conn.execute(
                """UPDATE tickets
                   SET ticket_status=?, assigned_team=?, updated_at=?, resolved_at=?
                   WHERE id=?""",
                (status, assigned_team, now, resolved_at, ticket_id),
            )
        else:
            cur = conn.execute(
                """UPDATE tickets
                   SET ticket_status=?, updated_at=?, resolved_at=?
                   WHERE id=?""",
                (status, now, resolved_at, ticket_id),
            )
        if cur.rowcount == 0:
            raise ValueError("Ticket not found.")


def delete_ticket(ticket_id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
        if cur.rowcount == 0:
            raise ValueError("Ticket not found.")


initialize_database()
