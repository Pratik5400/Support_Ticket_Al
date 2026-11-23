"""EV-specific deterministic routing for VoltWay Networks."""

TEAM_ROUTING = {
    "Payment & Billing": "Payment Support",
    "Charging Failure": "Technical Operations",
    "Station Availability": "Network Operations",
    "Refund & Transaction": "Finance Support",
    "Account & Application": "Account Support",
    "Safety Incident": "Safety Operations",
    "General Inquiry": "General Support",

    # Backward compatibility with tickets created before the EV upgrade.
    "Billing": "Payment Support",
    "Technical Support": "Technical Operations",
    "Account Access": "Account Support",
}

TEAM_SLAS = {
    "Safety Operations": "Immediate human response",
    "Payment Support": "2 hours",
    "Technical Operations": "2 hours",
    "Network Operations": "1 hour",
    "Finance Support": "4 hours",
    "Account Support": "4 hours",
    "General Support": "8 hours",
}

CATEGORY_ALIASES = {
    "billing": "Payment & Billing",
    "payment": "Payment & Billing",
    "payment and billing": "Payment & Billing",
    "technical support": "Charging Failure",
    "technical issue": "Charging Failure",
    "account access": "Account & Application",
    "general inquiry": "General Inquiry",
    "refund": "Refund & Transaction",
}

SAFETY_TERMS = (
    "smoke", "fire", "burning smell", "overheating", "overheated",
    "electric shock", "electrical shock", "sparks", "exposed wire",
    "electricity leak", "caught fire"
)
SECURITY_TERMS = (
    "account takeover", "hacked", "unauthorized access",
    "account compromised", "stolen password", "phishing"
)
LEGAL_TERMS = (
    "lawyer", "legal action", "lawsuit", "take you to court",
    "regulatory violation", "report to regulator", "chargeback threat"
)
OUTAGE_TERMS = (
    "entire network is down", "all stations are offline",
    "multiple stations offline", "critical network outage",
    "network-wide outage", "entire charging network"
)
PAYMENT_HIGH_TERMS = (
    "payment deducted", "amount deducted", "charged but",
    "paid but", "charged twice", "double charge",
    "payment taken", "money deducted", "amount has been deducted",
    "deducted from my account", "deducted from my bank", "paid ₹", "paid rs"
)
STATION_TERMS = (
    "station offline", "station is offline", "station unavailable",
    "charger unavailable", "charging station is down", "station is down"
)
CHARGING_FAILURE_TERMS = (
    "charging did not start",
    "charging does not start",
    "charging doesn't start",
    "charging didn't start",
    "charger did not start",
    "charger does not start",
    "charger doesn't start",
    "charger didn't start",
    "charging stopped",
    "charging failed",
    "unable to charge",
    "charger not working",
    "charging session failed",
    "session never started",
    "connector error",
    "connector issue",
    "charger error",
    "charger displays an error",
    "charger showing an error",
    "charging error",
    "charging malfunction",
)


def _contains(text, terms):
    return any(term in text for term in terms)


def _normalise_category(category):
    value = str(category or "General Inquiry").strip()
    if value in TEAM_ROUTING:
        return value
    return CATEGORY_ALIASES.get(value.lower(), "General Inquiry")


def route_ticket(result, ticket_text):
    """Apply VoltWay category routing, priority and escalation rules."""
    updated = dict(result or {})
    text = str(ticket_text or "").lower()
    category = _normalise_category(updated.get("category"))
    urgency = str(updated.get("urgency", "Medium")).strip().title()

    # Specific business signals take precedence over generic model labels.
    if _contains(text, SAFETY_TERMS):
        category = "Safety Incident"
    elif _contains(text, SECURITY_TERMS):
        category = "Account & Application"
    elif _contains(text, PAYMENT_HIGH_TERMS):
        category = "Payment & Billing"
    elif _contains(text, STATION_TERMS):
        category = "Station Availability"
    elif _contains(text, CHARGING_FAILURE_TERMS):
        category = "Charging Failure"
    elif _contains(text, ("refund", "money not returned", "refund pending")):
        category = "Refund & Transaction"
    elif _contains(text, ("payment", "billing", "transaction", "invoice")):
        category = "Payment & Billing"

    # Keep urgency values inside the application's supported set.
    if urgency not in {"Low", "Medium", "High", "Critical"}:
        urgency = "Medium"

    rule_triggered = "Standard EV Support Routing"
    escalation_status = "Normal"
    escalate = False
    assigned_team = TEAM_ROUTING.get(category, "General Support")
    reason = "Standard workflow: routed to the relevant VoltWay support department."
    sla = TEAM_SLAS.get(assigned_team, "8 hours")

    # Priority order: physical safety, account security, legal, network-wide outage,
    # then issue-specific priority.
    if category == "Safety Incident":
        urgency = "Critical"
        assigned_team = "Safety Operations"
        escalation_status = "Escalated"
        escalate = True
        reason = (
            "Safety escalation: possible smoke, fire, overheating, electric shock "
            "or electrical hazard. Immediate human intervention is required. "
            "The customer should move away from the equipment and contact local emergency services if in danger."
        )
        rule_triggered = "EV Rule 1: Safety Incident"
        sla = "Immediate human response"

    elif _contains(text, SECURITY_TERMS):
        urgency = "Critical"
        assigned_team = "Account Support"
        escalation_status = "Escalated"
        escalate = True
        reason = "Account security concern detected. Human verification is required."
        rule_triggered = "EV Rule 2: Account Security"

    elif _contains(text, LEGAL_TERMS):
        assigned_team = TEAM_ROUTING.get(category, "General Support")
        escalation_status = "Escalated"
        escalate = True
        reason = "Explicit legal or regulatory threat requires administrator review."
        rule_triggered = "EV Rule 3: Legal/Regulatory Review"

    elif _contains(text, OUTAGE_TERMS):
        category = "Station Availability"
        urgency = "Critical"
        assigned_team = "Network Operations"
        escalation_status = "Escalated"
        escalate = True
        reason = "Potential network-wide charging outage requires urgent operations review."
        rule_triggered = "EV Rule 4: Network Outage"

    else:
        assigned_team = TEAM_ROUTING.get(category, "General Support")
        if category == "Payment & Billing" and _contains(text, PAYMENT_HIGH_TERMS):
            urgency = "High"
            escalation_status = "Priority Review"
            reason = "Payment may have been deducted without a successful charging session. Verify the transaction before any refund decision."
            rule_triggered = "EV Rule 5: Payment/Charging Mismatch"
        elif category == "Charging Failure":
            urgency = "High" if urgency in {"Low", "Medium"} else urgency
            escalation_status = "Priority Review" if urgency == "High" else "Escalated"
            escalate = urgency == "Critical"
            reason = "Charging session failure requires technical investigation."
            rule_triggered = "EV Rule 6: Charging Failure"
        elif category == "Station Availability":
            urgency = "High" if urgency in {"Low", "Medium"} else urgency
            escalation_status = "Priority Review" if urgency == "High" else "Escalated"
            escalate = urgency == "Critical"
            reason = "Station availability issue requires network operations review."
            rule_triggered = "EV Rule 7: Station Availability"
        elif urgency == "Critical":
            escalation_status = "Escalated"
            escalate = True
            reason = "Critical urgency requires immediate human review."
            rule_triggered = "EV Rule 8: Critical SLA"
        elif urgency == "High":
            escalation_status = "Priority Review"
            reason = "High-priority ticket requires expedited review."
            rule_triggered = "EV Rule 9: High Priority"

    # Calculate SLA after routing so every branch, including safety/legal/security,
    # always has a defined SLA value.
    if escalation_status == "Escalated":
        sla = "Immediate human response" if urgency == "Critical" else "30 minutes"
    elif escalation_status == "Priority Review":
        sla = "2 hours (priority review)"
    else:
        sla = TEAM_SLAS.get(assigned_team, "8 hours")

    updated["category"] = category
    updated["urgency"] = urgency
    updated["assigned_team"] = assigned_team
    updated["escalation_status"] = escalation_status
    updated["escalate"] = escalate
    updated["escalation_reason"] = reason
    updated["rule_triggered"] = rule_triggered
    updated["sla_target"] = sla
    return updated
