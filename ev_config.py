
# ev_config.py
"""
Business configuration for SupportAI.
Fictional EV charging operator: VoltWay Networks.
"""

BUSINESS_NAME = "VoltWay Networks"
BUSINESS_DESCRIPTION = (
    "An EV charging network operator providing public "
    "electric vehicle charging services."
)

BUSINESS_CITIES = [
    "Pune",
    "Mumbai",
    "Nashik",
]

TICKET_CATEGORIES = [
    "Payment & Billing",
    "Charging Failure",
    "Station Availability",
    "Refund & Transaction",
    "Account & Application",
    "Safety Incident",
    "General Inquiry",
]

SUPPORT_TEAMS = [
    "Payment Support",
    "Technical Operations",
    "Network Operations",
    "Finance Support",
    "Account Support",
    "Safety Operations",
    "General Support",
]

URGENCY_LEVELS = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

TICKET_STATUSES = [
    "Open",
    "In Progress",
    "Awaiting Customer",
    "Resolved",
    "Closed",
]

# Fictional charging stations for the jury demonstration.
# These are sample records, not real operating stations.

SAMPLE_STATIONS = [
    {
        "station_id": "VLT-PUN-001",
        "station_name": "Baner Central Charging Hub",
        "city": "Pune",
        "area": "Baner",
        "charger_type": "DC Fast Charger",
        "power_kw": 60,
        "station_status": "Operational",
    },
    {
        "station_id": "VLT-PUN-002",
        "station_name": "Hinjawadi Tech Park Hub",
        "city": "Pune",
        "area": "Hinjawadi",
        "charger_type": "DC Fast Charger",
        "power_kw": 120,
        "station_status": "Operational",
    },
    {
        "station_id": "VLT-PUN-003",
        "station_name": "Kothrud Public Charging Point",
        "city": "Pune",
        "area": "Kothrud",
        "charger_type": "AC Charger",
        "power_kw": 22,
        "station_status": "Maintenance",
    },
    {
        "station_id": "VLT-MUM-001",
        "station_name": "Andheri Metro Charging Hub",
        "city": "Mumbai",
        "area": "Andheri",
        "charger_type": "DC Fast Charger",
        "power_kw": 60,
        "station_status": "Operational",
    },
    {
        "station_id": "VLT-MUM-002",
        "station_name": "Bandra Business District Hub",
        "city": "Mumbai",
        "area": "Bandra",
        "charger_type": "DC Fast Charger",
        "power_kw": 120,
        "station_status": "Operational",
    },
    {
        "station_id": "VLT-NSK-001",
        "station_name": "Nashik Road Charging Hub",
        "city": "Nashik",
        "area": "Nashik Road",
        "charger_type": "AC Charger",
        "power_kw": 22,
        "station_status": "Operational",
    },
]

# Issue keywords used by the internal fallback classifier and routing logic.
ISSUE_KEYWORDS = {
    "Safety Incident": [
        "smoke", "fire", "burning smell", "burning", "overheating", "overheated",
        "electric shock", "electrical shock", "sparks", "sparking", "exposed wire",
        "electricity leak", "caught fire", "explosion",
    ],
    "Account & Application": [
        "fraudulent transaction", "fraudulent", "fraud", "unauthorized transaction",
        "unauthorized access", "account takeover", "hacked", "hack", "compromised",
        "account compromised", "stolen password", "phishing", "accessed my account",
        "login", "log in", "cannot log in", "can't log in", "password", "reset password",
        "app crash", "app crashes", "application crash", "application crashes",
        "application not working", "app not working", "cannot access account",
        "can't access account", "locked out", "account access",
    ],
    "Payment & Billing": [
        "payment deducted", "amount deducted", "money deducted", "charged twice",
        "double charge", "charged but", "paid but", "payment failed", "payment taken",
        "deducted from my account", "deducted from my bank", "amount has been deducted",
        "paid ₹", "paid rs", "billing", "invoice", "double subscription",
    ],
    "Refund & Transaction": [
        "refund", "money not returned", "refund pending", "refund status",
        "transaction reference", "reverse charge", "chargeback",
    ],
    "Charging Failure": [
        "connector error", "connector issue", "connector problem", "cable error",
        "cable stuck", "plug error", "plug issue", "charger displays a connector error",
        "charger displays an error", "charger showing an error", "charger error",
        "charging error", "charging did not start", "charging does not start",
        "charging doesn't start", "charging didn't start", "charger did not start",
        "charger does not start", "charger doesn't start", "charger didn't start",
        "did not initiate", "does not initiate", "charging stopped", "charging failed",
        "session failed", "charging session failed", "session never started",
        "unable to charge", "charger not working", "charging malfunction",
        "reconnecting the cable",
    ],
    "Station Availability": [
        "station offline", "station is offline", "charger unavailable",
        "station unavailable", "station not working", "charging station is down",
        "station is down", "network-wide outage", "entire network is down",
        "all stations are offline", "multiple stations offline",
    ],
    "General Inquiry": [
        "general question", "inquiry", "support hours", "working hours",
        "information about", "just asking", "pricing question", "tariff",
    ],
}
