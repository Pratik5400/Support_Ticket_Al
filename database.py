import os
import sys
from pathlib import Path
import re
import hmac
import hashlib
import secrets
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
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

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

try:
    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000, connectTimeoutMS=4000)
    _db = _client[MONGO_DB_NAME]
    _users = _db["users"]
    _tickets = _db["tickets"]
    _counters = _db["counters"]
except Exception as _client_err:
    MONGO_ERROR = str(_client_err)


def get_database():
    return _db


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


def _next_id(counter_name):
    counter = _counters.find_one_and_update(
        {"_id": counter_name}, {"$inc": {"sequence": 1}},
        upsert=True, return_document=ReturnDocument.AFTER
    )
    return int(counter["sequence"])


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


def _provision_admin():
    name = os.getenv("ADMIN_NAME", "Support Administrator").strip()
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")
    if not email or not password:
        return
    if len(password) < 8:
        raise ValueError("ADMIN_PASSWORD must be at least 8 characters.")
    if _users.find_one({"email": email}, {"_id": 1}):
        return
    try:
        _users.insert_one({
            "id": _next_id("users"),
            "name": name or "Support Administrator",
            "email": email,
            "password_hash": _hash_password(password),
            "role": "admin",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
    except DuplicateKeyError:
        return


def initialize_database():
    global MONGO_CONNECTED, MONGO_ERROR
    if _client is None:
        MONGO_CONNECTED = False
        return False
    try:
        _client.admin.command("ping")
        _users.create_index("id", unique=True)
        _users.create_index("email", unique=True)
        _tickets.create_index("id", unique=True)
        _tickets.create_index([("user_id", 1), ("id", -1)])
        _tickets.create_index([("ticket_status", 1), ("sla_due_at", 1)])
        _provision_admin()
        MONGO_CONNECTED = True
        MONGO_ERROR = None
        return True
    except PyMongoError as exc:
        MONGO_CONNECTED = False
        MONGO_ERROR = str(exc)
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
    try:
        user_id = _next_id("users")
        _users.insert_one({
            "id": user_id, "name": name, "email": email,
            "password_hash": _hash_password(password), "role": "user",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
        return user_id
    except DuplicateKeyError:
        raise ValueError("An account with this email already exists.") from None


def authenticate_user(email, password):
    email = (email or "").strip().lower()
    row = _users.find_one({"email": email})
    if not row or not _verify_password(password or "", row.get("password_hash")):
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
    ticket_id = _next_id("tickets")
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
        "sla_due_at": _sla_due_datetime(result), "resolved_at": None,
    }
    _tickets.insert_one(document)
    return ticket_id


def _clean_document(document):
    if not document:
        return None
    document.pop("_id", None)
    return document


def get_all_tickets():
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
        output.append(_clean_document(row))
    return output


def get_user_tickets(user_id):
    return [_clean_document(row) for row in _tickets.find({"user_id": user_id}).sort("id", -1)]


def get_ticket(ticket_id):
    try:
        ticket_id = int(ticket_id)
    except (TypeError, ValueError):
        return None
    return _clean_document(_tickets.find_one({"id": ticket_id}))


def update_approval_status(ticket_id, status):
    if status not in {"Pending", "Approved", "Rejected"}:
        raise ValueError("Invalid approval status.")
    result = _tickets.update_one(
        {"id": int(ticket_id)},
        {"$set": {"approval_status": status, "updated_at": datetime.now().isoformat(timespec="seconds")}}
    )
    if result.matched_count == 0:
        raise ValueError("Ticket not found.")


def update_ticket_reply(ticket_id, draft_reply):
    draft_reply = (draft_reply or "").strip()
    if not draft_reply:
        raise ValueError("Reply cannot be empty.")
    result = _tickets.update_one(
        {"id": int(ticket_id)},
        {"$set": {"draft_reply": draft_reply, "updated_at": datetime.now().isoformat(timespec="seconds")}}
    )
    if result.matched_count == 0:
        raise ValueError("Ticket not found.")


def update_ticket_status(ticket_id, status, assigned_team=None):
    allowed = {"Open", "In Progress", "Awaiting Customer", "Resolved", "Closed"}
    if status not in allowed:
        raise ValueError("Invalid ticket status.")
    now = datetime.now().isoformat(timespec="seconds")
    updates = {
        "ticket_status": status, "updated_at": now,
        "resolved_at": now if status in {"Resolved", "Closed"} else None,
    }
    if assigned_team:
        updates["assigned_team"] = assigned_team
    result = _tickets.update_one({"id": int(ticket_id)}, {"$set": updates})
    if result.matched_count == 0:
        raise ValueError("Ticket not found.")


def delete_ticket(ticket_id):
    result = _tickets.delete_one({"id": int(ticket_id)})
    if result.deleted_count == 0:
        raise ValueError("Ticket not found.")


initialize_database()
