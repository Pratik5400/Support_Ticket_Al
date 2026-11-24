import os
import sys
from pathlib import Path
import re
import hmac
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta

# Automatically ensure local virtualenv packages are discoverable
_venv_site = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
if _venv_site.is_dir() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    def load_dotenv(dotenv_path=".env", override=False):
        p = Path(dotenv_path)
        if not p.is_absolute():
            p = Path(__file__).resolve().parent / dotenv_path
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#") and "=" in s:
                        k, v = s.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and (override or k not in os.environ):
                            os.environ[k] = v
    load_dotenv()

# Sync Streamlit Cloud secrets to environment variables if available
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, str) and k not in os.environ:
                os.environ[k] = v
except Exception:
    pass

SQLITE_PATH = Path(__file__).resolve().parent / "support_tickets.db"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "voltway_supportai")
PBKDF2_ITERATIONS = 310_000

MONGO_CONNECTED = False
MONGO_ERROR = None

_client = None
_db = None
_users = None
_tickets = None
_counters = None


def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH, timeout=20)
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


def _sla_due_datetime(result):
    label = str((result or {}).get("sla_target") or "8 hours").lower()
    hours_match = re.search(r"(\d+(?:\.\d+)?)\s*hours?", label)
    minutes_match = re.search(r"(\d+(?:\.\d+)?)\s*minutes?", label)
    if hours_match:
        duration = timedelta(hours=float(hours_match.group(1)))
    elif minutes_match:
        duration = timedelta(minutes=float(minutes_match.group(1)))
    elif "immediate" in label:
        duration = timedelta(minutes=30)
    else:
        duration = timedelta(hours=8)
    return (datetime.now() + duration).isoformat(timespec="seconds")


def _next_mongo_id(counter_name):
    from pymongo import ReturnDocument
    counter = _counters.find_one_and_update(
        {"_id": counter_name}, {"$inc": {"sequence": 1}},
        upsert=True, return_document=ReturnDocument.AFTER
    )
    return int(counter["sequence"])


def _clean_mongo_doc(document):
    if not document:
        return None
    document.pop("_id", None)
    return document


def _provision_admin():
    name = os.getenv("ADMIN_NAME", "Support Administrator").strip()
    email = os.getenv("ADMIN_EMAIL", "admin@supportai.com").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "YourActualStrongPassword123")
    if not email or not password:
        return
    if len(password) < 8:
        return

    if MONGO_CONNECTED:
        from pymongo.errors import DuplicateKeyError
        if _users.find_one({"email": email}, {"_id": 1}):
            return
        try:
            _users.insert_one({
                "id": _next_mongo_id("users"),
                "name": name or "Support Administrator",
                "email": email,
                "password_hash": _hash_password(password),
                "role": "admin",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
        except DuplicateKeyError:
            pass
    else:
        with get_sqlite_conn() as conn:
            row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin')",
                    (name or "Support Administrator", email, _hash_password(password)),
                )


def _init_sqlite():
    with get_sqlite_conn() as conn:
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


def initialize_database():
    global MONGO_CONNECTED, MONGO_ERROR, _client, _db, _users, _tickets, _counters
    
    # Try connecting to MongoDB first
    try:
        from pymongo import MongoClient
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500, connectTimeoutMS=2500)
        _client.admin.command("ping")
        _db = _client[MONGO_DB_NAME]
        _users = _db["users"]
        _tickets = _db["tickets"]
        _counters = _db["counters"]
        _users.create_index("id", unique=True)
        _users.create_index("email", unique=True)
        _tickets.create_index("id", unique=True)
        _tickets.create_index([("user_id", 1), ("id", -1)])
        _tickets.create_index([("ticket_status", 1), ("sla_due_at", 1)])
        MONGO_CONNECTED = True
        MONGO_ERROR = None
        _provision_admin()
        return True
    except Exception as exc:
        MONGO_CONNECTED = False
        MONGO_ERROR = str(exc)
        # Seamlessly fallback to SQLite
        try:
            _init_sqlite()
            _provision_admin()
        except Exception:
            pass
        return False


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

    if MONGO_CONNECTED:
        from pymongo.errors import DuplicateKeyError
        try:
            user_id = _next_mongo_id("users")
            _users.insert_one({
                "id": user_id, "name": name, "email": email,
                "password_hash": _hash_password(password), "role": "user",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
            return user_id
        except DuplicateKeyError:
            raise ValueError("An account with this email already exists.") from None
    else:
        try:
            with get_sqlite_conn() as conn:
                cursor = conn.execute(
                    "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'user')",
                    (name, email, _hash_password(password)),
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("An account with this email already exists.") from None


def authenticate_user(email, password):
    email = (email or "").strip().lower()
    if MONGO_CONNECTED:
        row = _users.find_one({"email": email})
        if not row or not _verify_password(password or "", row.get("password_hash")):
            return None
        return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}
    else:
        with get_sqlite_conn() as conn:
            row = conn.execute(
                "SELECT id,name,email,password_hash,role FROM users WHERE email = ?", (email,)
            ).fetchone()
        if not row or not _verify_password(password or "", row["password_hash"]):
            return None
        return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}


def save_ticket(ticket_text, result, user_id=None, subject="Support request",
                station_id=None, station_name=None, station_city=None,
                transaction_id=None, session_id=None, vehicle_model=None):
    required = ("category", "urgency", "sentiment", "summary", "draft_reply")
    missing = [field for field in required if field not in result]
    if missing:
        raise ValueError("Analysis missing: " + ", ".join(missing))

    now = datetime.now().isoformat(timespec="seconds")
    sla_due = _sla_due_datetime(result)

    if MONGO_CONNECTED:
        ticket_id = _next_mongo_id("tickets")
        document = {
            "id": ticket_id, "ticket_text": ticket_text,
            "category": result["category"], "urgency": result["urgency"],
            "sentiment": result["sentiment"], "summary": result["summary"],
            "draft_reply": result["draft_reply"],
            "escalate": bool(result.get("escalate", False)),
            "escalation_reason": result.get("escalation_reason"),
            "approval_status": "Pending",
            "assigned_team": result.get("assigned_team", "General Support"),
            "escalation_status": result.get("escalation_status", "Normal"),
            "rule_triggered": result.get("rule_triggered", "Standard Routing"),
            "sla_target": result.get("sla_target", "8 hours"),
            "user_id": user_id, "subject": (subject or "Support request").strip(),
            "ticket_status": "Open",
            "analysis_mode": result.get("analysis_mode", "Rule-Based Fallback"),
            "model_used": result.get("model_used"),
            "created_at": now, "updated_at": now,
            "station_id": station_id, "station_name": station_name,
            "station_city": station_city, "transaction_id": transaction_id,
            "session_id": session_id, "vehicle_model": vehicle_model,
            "sla_due_at": sla_due, "resolved_at": None,
        }
        _tickets.insert_one(document)
        return ticket_id
    else:
        with get_sqlite_conn() as conn:
            cur = conn.execute("""
                INSERT INTO tickets (
                    ticket_text, category, urgency, sentiment,
                    summary, draft_reply, escalate, escalation_reason,
                    approval_status, assigned_team, escalation_status,
                    rule_triggered, sla_target, user_id, subject,
                    ticket_status, analysis_mode, model_used, updated_at,
                    station_id, station_name, station_city,
                    transaction_id, session_id, vehicle_model,
                    created_at, sla_due_at
                )
                VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    'Open',?,?,?,
                    ?,?,?,?,?,?,?,?
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
                now,
                station_id,
                station_name,
                station_city,
                transaction_id,
                session_id,
                vehicle_model,
                now,
                sla_due,
            ))
            return cur.lastrowid


def get_all_tickets():
    if MONGO_CONNECTED:
        rows = list(_tickets.find().sort("id", -1))
        user_ids = {row.get("user_id") for row in rows if row.get("user_id") is not None}
        users_by_id = {}
        if user_ids:
            for user in _users.find(
                {"id": {"$in": list(user_ids)}},
                {"_id": 0, "id": 1, "name": 1, "email": 1}
            ):
                users_by_id[user["id"]] = user
        output = []
        for row in rows:
            user = users_by_id.get(row.get("user_id"), {})
            row["customer_name"] = user.get("name")
            row["customer_email"] = user.get("email")
            output.append(_clean_mongo_doc(row))
        return output
    else:
        with get_sqlite_conn() as conn:
            rows = conn.execute("""
                SELECT t.*, u.name AS customer_name, u.email AS customer_email
                FROM tickets t LEFT JOIN users u ON u.id=t.user_id
                ORDER BY t.id DESC
            """).fetchall()
            return [dict(row) for row in rows]


def get_user_tickets(user_id):
    if MONGO_CONNECTED:
        return [_clean_mongo_doc(row) for row in _tickets.find({"user_id": user_id}).sort("id", -1)]
    else:
        with get_sqlite_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM tickets WHERE user_id=? ORDER BY id DESC", (user_id,)
            ).fetchall()
            return [dict(row) for row in rows]


def get_ticket(ticket_id):
    try:
        ticket_id = int(ticket_id)
    except (TypeError, ValueError):
        return None
    if MONGO_CONNECTED:
        return _clean_mongo_doc(_tickets.find_one({"id": ticket_id}))
    else:
        with get_sqlite_conn() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
            return dict(row) if row else None


def update_approval_status(ticket_id, status):
    if status not in {"Pending", "Approved", "Rejected"}:
        raise ValueError("Invalid approval status.")
    if MONGO_CONNECTED:
        result = _tickets.update_one(
            {"id": int(ticket_id)},
            {"$set": {"approval_status": status, "updated_at": datetime.now().isoformat(timespec="seconds")}}
        )
        if result.matched_count == 0:
            raise ValueError("Ticket not found.")
    else:
        with get_sqlite_conn() as conn:
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
    if MONGO_CONNECTED:
        result = _tickets.update_one(
            {"id": int(ticket_id)},
            {"$set": {"draft_reply": draft_reply, "updated_at": datetime.now().isoformat(timespec="seconds")}}
        )
        if result.matched_count == 0:
            raise ValueError("Ticket not found.")
    else:
        with get_sqlite_conn() as conn:
            cur = conn.execute(
                "UPDATE tickets SET draft_reply=?, updated_at=? WHERE id=?",
                (draft_reply, datetime.now().isoformat(timespec="seconds"), ticket_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Ticket not found.")


def update_ticket_status(ticket_id, status, assigned_team=None):
    allowed = {"Open", "In Progress", "Awaiting Customer", "Resolved", "Closed"}
    if status not in allowed:
        raise ValueError("Invalid ticket status.")
    now = datetime.now().isoformat(timespec="seconds")
    if MONGO_CONNECTED:
        updates = {
            "ticket_status": status, "updated_at": now,
            "resolved_at": now if status in {"Resolved", "Closed"} else None,
        }
        if assigned_team:
            updates["assigned_team"] = assigned_team
        result = _tickets.update_one({"id": int(ticket_id)}, {"$set": updates})
        if result.matched_count == 0:
            raise ValueError("Ticket not found.")
    else:
        with get_sqlite_conn() as conn:
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
    if MONGO_CONNECTED:
        result = _tickets.delete_one({"id": int(ticket_id)})
        if result.deleted_count == 0:
            raise ValueError("Ticket not found.")
    else:
        with get_sqlite_conn() as conn:
            cur = conn.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
            if cur.rowcount == 0:
                raise ValueError("Ticket not found.")


# Initialize on import
initialize_database()
