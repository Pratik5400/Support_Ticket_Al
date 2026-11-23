
from llm_service import analyze_ticket
from routing import route_ticket

examples = [
    "I was charged twice for my monthly subscription.",
    "Someone made a fraudulent transaction and accessed my account.",
    "My application crashes whenever I open it.",
    "I have a question about my subscription.",
    "I visited the Baner Central Charging Hub today to charge my Tata Nexon EV. The charger displays a connector error and charging does not start. I tried reconnecting the cable twice, but the problem continues. Please resolve this issue."
]

for number, message in enumerate(examples, start=1):

    # Step 1: Classify using local fallback
    result = analyze_ticket(message, fallback_mode=True)

    # Step 2: Apply business routing rules
    routed_result = route_ticket(result, message)

    print(f"\n{'=' * 45}")
    print(f"TEST {number}")
    print(f"{'=' * 45}")

    print("Mode:", routed_result.get("analysis_mode"))
    print("Category:", routed_result.get("category"))
    print("Urgency:", routed_result.get("urgency"))
    print("Assigned Team:", routed_result.get("assigned_team"))
    print("Escalation:", routed_result.get("escalation_status"))
    print("SLA Target:", routed_result.get("sla_target"))
    print("Routing Rule:", routed_result.get("rule_triggered"))
    print("Reason:", routed_result.get("escalation_reason"))
