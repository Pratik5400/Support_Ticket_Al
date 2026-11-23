from llm_service import analyze_ticket
from routing import route_ticket

cases = [
    (
        "I paid ₹500, but the charger did not initiate my charging session. "
        "The amount has been deducted from my account.",
        "Payment & Billing", "High", "Payment Support", "Priority Review"
    ),
    (
        "The charger at my station is not working and my charging session failed.",
        "Charging Failure", "High", "Technical Operations", "Priority Review"
    ),
    (
        "The charging station is offline and unavailable.",
        "Station Availability", "High", "Network Operations", "Priority Review"
    ),
    (
        "There is smoke and a burning smell coming from the charger.",
        "Safety Incident", "Critical", "Safety Operations", "Escalated"
    ),
    (
        "My refund is still pending after the failed charging session.",
        "Refund & Transaction", "Medium", "Finance Support", "Normal"
    ),
    (
        "There is a network-wide outage and all stations are offline.",
        "Station Availability", "Critical", "Network Operations", "Escalated"
    ),
    (
        "Someone has hacked my account and there is unauthorized access.",
        "Account & Application", "Critical", "Account Support", "Escalated"
    ),
]

for index, (message, category, urgency, team, escalation) in enumerate(cases, 1):
    result = analyze_ticket(message, fallback_mode=True)
    result = route_ticket(result, message)

    assert result["category"] == category, (index, result["category"], category)
    assert result["urgency"] == urgency, (index, result["urgency"], urgency)
    assert result["assigned_team"] == team, (index, result["assigned_team"], team)
    assert result["escalation_status"] == escalation, (
        index, result["escalation_status"], escalation
    )
    assert result["draft_reply"], (index, "empty reply")

    print(
        f"TEST {index} PASSED | {result['category']} | {result['urgency']} | "
        f"{result['assigned_team']} | {result['escalation_status']}"
    )

print("\\nAll VoltWay fallback and routing tests passed.")
