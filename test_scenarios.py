"""
test_scenarios.py - Automated verification of the 6 core VoltWay Networks business scenarios.
Tests Category, Urgency, Assigned Team, Escalation Status, and SLA Target.
Tests both Rule-Based Fallback and AI mode handling.
"""

from llm_service import analyze_ticket
from routing import route_ticket

SCENARIOS = [
    {
        "id": 1,
        "name": "Payment deducted but charging did not start",
        "subject": "Payment deducted but charger did not start",
        "text": "I visited the Baner Central Charging Hub. I paid ₹500, but the charger did not initiate my charging session. The amount has been deducted from my bank account. Please investigate.",
        "expected": {
            "category": "Payment & Billing",
            "urgency": "High",
            "assigned_team": "Payment Support",
            "escalation_status": "Priority Review",
            "sla_target": "2 hours (priority review)",
        }
    },
    {
        "id": 2,
        "name": "EV charger connector error",
        "subject": "EV charger connector error",
        "text": "I visited the Baner Central Charging Hub today to charge my Tata Nexon EV. The charger displays a connector error and charging does not start. I tried reconnecting the cable twice, but the problem continues.",
        "expected": {
            "category": "Charging Failure",
            "urgency": "High",
            "assigned_team": "Technical Operations",
            "escalation_status": "Priority Review",
            "sla_target": "2 hours (priority review)",
        }
    },
    {
        "id": 3,
        "name": "Charging session failure",
        "subject": "Charging session failed abruptly",
        "text": "My DC fast charging session failed after 5 minutes at Hinjawadi Tech Park Hub. The charger stopped delivering power and displayed session failed error.",
        "expected": {
            "category": "Charging Failure",
            "urgency": "High",
            "assigned_team": "Technical Operations",
            "escalation_status": "Priority Review",
            "sla_target": "2 hours (priority review)",
        }
    },
    {
        "id": 4,
        "name": "Duplicate payment",
        "subject": "Charged twice for single charging session",
        "text": "I was charged twice for my charging session yesterday. Two deductions of ₹650 appear on my card statement for a single session. Please check this double charge.",
        "expected": {
            "category": "Payment & Billing",
            "urgency": "High",
            "assigned_team": "Payment Support",
            "escalation_status": "Priority Review",
            "sla_target": "2 hours (priority review)",
        }
    },
    {
        "id": 5,
        "name": "Fraudulent transaction or unauthorized account access",
        "subject": "Unauthorized access and fraudulent transaction",
        "text": "Someone made a fraudulent transaction on my VoltWay account and accessed my account without authorization. I suspect my account has been compromised.",
        "expected": {
            "category": "Account & Application",
            "urgency": "Critical",
            "assigned_team": "Account Support",
            "escalation_status": "Escalated",
            "sla_target": "Immediate human response",
        }
    },
    {
        "id": 6,
        "name": "General customer inquiry",
        "subject": "Question about charging tariffs and support hours",
        "text": "Hello VoltWay support, I would like to know the current pricing tariff per kWh at your Mumbai DC fast charging hubs and your customer support working hours.",
        "expected": {
            "category": "General Inquiry",
            "urgency": ["Low", "Medium"],  # Low or Medium is valid for general questions
            "assigned_team": "General Support",
            "escalation_status": "Normal",
            "sla_target": "8 hours",
        }
    },
]


def run_scenario_tests(fallback_mode=True):
    mode_name = "Rule-Based Fallback" if fallback_mode else "Live Gemini AI / Auto-Fallback"
    print(f"\n{'=' * 65}")
    print(f"RUNNING 6 CORE SCENARIOS IN [{mode_name.upper()}] MODE")
    print(f"{'=' * 65}")

    all_passed = True
    for scenario in SCENARIOS:
        full_text = f"{scenario['subject']}\n{scenario['text']}"
        raw_result = analyze_ticket(full_text, fallback_mode=fallback_mode)
        routed = route_ticket(raw_result, full_text)

        expected = scenario["expected"]
        failures = []

        if routed.get("category") != expected["category"]:
            failures.append(f"category: got {routed.get('category')!r}, expected {expected['category']!r}")

        exp_urgency = expected["urgency"]
        actual_urgency = routed.get("urgency")
        if isinstance(exp_urgency, list):
            if actual_urgency not in exp_urgency:
                failures.append(f"urgency: got {actual_urgency!r}, expected one of {exp_urgency!r}")
        elif actual_urgency != exp_urgency:
            failures.append(f"urgency: got {actual_urgency!r}, expected {exp_urgency!r}")

        if routed.get("assigned_team") != expected["assigned_team"]:
            failures.append(f"assigned_team: got {routed.get('assigned_team')!r}, expected {expected['assigned_team']!r}")

        if routed.get("escalation_status") != expected["escalation_status"]:
            failures.append(f"escalation_status: got {routed.get('escalation_status')!r}, expected {expected['escalation_status']!r}")

        if routed.get("sla_target") != expected["sla_target"]:
            failures.append(f"sla_target: got {routed.get('sla_target')!r}, expected {expected['sla_target']!r}")

        if not failures:
            print(f"  [PASS] Scenario {scenario['id']}: {scenario['name']}")
            print(f"         Category: {routed.get('category')} | Urgency: {routed.get('urgency')} | Team: {routed.get('assigned_team')} | Escalation: {routed.get('escalation_status')} | SLA: {routed.get('sla_target')}")
        else:
            all_passed = False
            print(f"  [FAIL] Scenario {scenario['id']}: {scenario['name']}")
            for failure in failures:
                print(f"         - {failure}")

    return all_passed


if __name__ == "__main__":
    passed_fallback = run_scenario_tests(fallback_mode=True)
    passed_live = run_scenario_tests(fallback_mode=False)

    print(f"\n{'=' * 65}")
    print(f"FINAL RESULT: Fallback={passed_fallback}, Live/Resilient={passed_live}")
    print(f"{'=' * 65}")
    if not (passed_fallback and passed_live):
        exit(1)
