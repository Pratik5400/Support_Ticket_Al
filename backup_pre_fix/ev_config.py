
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

# Issue keywords used by the internal fallback classifier.
ISSUE_KEYWORDS = {
    "Safety Incident": [
        "smoke", "fire", "burning smell", "overheating",
        "electric shock", "sparks", "exposed wire",
    ],
    "Payment & Billing": [
        "payment deducted", "charged twice", "double charge",
        "payment failed", "amount deducted", "billing",
    ],
    "Refund & Transaction": [
        "refund", "money not returned", "refund pending",
        "transaction reference",
    ],
    "Charging Failure": [
        "charging failed",
        "charger not working",
        "charging stopped",
        "session failed",
        "charging did not start",
        "charging does not start",
        "unable to charge",
        "connector error",
        "connector issue",
        "charger error",
        "charging error",
    ],
    "Station Availability": [
        "station offline", "charger unavailable",
        "station unavailable", "station not working",
    ],
    "Account & Application": [
        "login", "log in", "password", "app crash",
        "application not working", "cannot access account",
    ],
}
