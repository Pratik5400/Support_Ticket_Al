"""
test_workflows.py - End-to-end automated verification of Customer and Administrator workflows.
Ensures database consistency between customer and administrator views.
"""

from database import (
    authenticate_user,
    get_user_tickets,
    get_all_tickets,
    get_ticket,
    save_ticket,
    update_approval_status,
    update_ticket_reply,
    update_ticket_status,
    delete_ticket,
    get_connection,
)
from routing import route_ticket
from llm_service import analyze_ticket


def test_customer_and_admin_workflow():
    print("\n" + "=" * 65)
    print("VERIFYING CUSTOMER & ADMINISTRATOR WORKFLOWS")
    print("=" * 65)

    # 1. Verify admin user exists
    with get_connection() as conn:
        admin_row = conn.execute("SELECT id, name, email, role FROM users WHERE role='admin'").fetchone()
        assert admin_row is not None, "Admin user should exist in database"
        admin_id = admin_row["id"]
        print(f"  [PASS] Found Administrator: {admin_row['name']} ({admin_row['email']})")

        # Get or verify a customer user
        customer_row = conn.execute("SELECT id, name, email, role FROM users WHERE role='user'").fetchone()
        assert customer_row is not None, "Customer user should exist in database"
        customer_id = customer_row["id"]
        print(f"  [PASS] Found Customer: {customer_row['name']} ({customer_row['email']})")

    # 2. Customer submits a complaint
    subject = "EV charger connector error during DC fast charging"
    ticket_text = (
        "I visited Baner Central Charging Hub with my Tata Nexon EV. "
        "The charger displays a connector error and charging does not start. "
        "Please resolve this issue."
    )
    station_id = "VLT-PUN-001"
    station_name = "Baner Central Charging Hub"
    station_city = "Pune"
    transaction_id = "TXN-TEST-999"
    session_id = "SES-TEST-999"
    vehicle_model = "Tata Nexon EV"

    full_text = f"{subject}\n{ticket_text}"
    analysis = route_ticket(analyze_ticket(full_text, fallback_mode=True), full_text)

    ticket_id = save_ticket(
        ticket_text=ticket_text,
        result=analysis,
        user_id=customer_id,
        subject=subject,
        station_id=station_id,
        station_name=station_name,
        station_city=station_city,
        transaction_id=transaction_id,
        session_id=session_id,
        vehicle_model=vehicle_model,
    )
    print(f"  [PASS] Customer submitted ticket #{ticket_id}")

    try:
        # 3. Customer checks ticket history
        customer_tickets = get_user_tickets(customer_id)
        cust_ticket = next((t for t in customer_tickets if t["id"] == ticket_id), None)
        assert cust_ticket is not None, "Customer should see their submitted ticket in history"
        assert cust_ticket["ticket_status"] == "Open", "Initial ticket status should be Open"
        assert cust_ticket["approval_status"] == "Pending", "Initial response approval status should be Pending"
        assert cust_ticket["category"] == "Charging Failure", f"Expected Charging Failure, got {cust_ticket['category']}"
        assert cust_ticket["assigned_team"] == "Technical Operations", f"Expected Technical Operations, got {cust_ticket['assigned_team']}"
        assert cust_ticket["station_id"] == station_id
        assert cust_ticket["transaction_id"] == transaction_id
        print(f"  [PASS] Customer history reflects ticket #{ticket_id} with status=Open, approval=Pending")

        # 4. Administrator inspects submitted tickets
        admin_tickets = get_all_tickets()
        admin_ticket = next((t for t in admin_tickets if t["id"] == ticket_id), None)
        assert admin_ticket is not None, "Administrator should see the ticket in all tickets list"
        assert admin_ticket["summary"], "AI summary should be present"
        assert admin_ticket["urgency"] == "High"
        assert admin_ticket["escalation_status"] == "Priority Review"
        assert admin_ticket["sla_due_at"] is not None, "SLA due timestamp should be generated"
        print(f"  [PASS] Admin inspected ticket #{ticket_id}: AI summary, urgency, team, escalation and SLA present")

        # 5. Administrator edits suggested response
        updated_reply = (
            "Thank you for reaching out to VoltWay Networks. Our Technical Operations team has dispatched "
            "a field technician to inspect connector #2 at Baner Central Charging Hub. We apologize for the inconvenience."
        )
        update_ticket_reply(ticket_id, updated_reply)
        ticket_after_edit = get_ticket(ticket_id)
        assert ticket_after_edit["draft_reply"] == updated_reply, "Reply should be updated in database"
        assert ticket_after_edit["approval_status"] == "Pending", "Approval status should still be Pending until approved"
        print(f"  [PASS] Admin edited suggested response (saved to database)")

        # 6. Administrator approves response
        update_approval_status(ticket_id, "Approved")
        ticket_after_approval = get_ticket(ticket_id)
        assert ticket_after_approval["approval_status"] == "Approved", "Approval status should be Approved"
        print(f"  [PASS] Admin approved response (approval_status=Approved)")

        # 7. Verify customer now sees approved response
        cust_ticket_updated = next(t for t in get_user_tickets(customer_id) if t["id"] == ticket_id)
        assert cust_ticket_updated["approval_status"] == "Approved"
        assert cust_ticket_updated["draft_reply"] == updated_reply
        print(f"  [PASS] Customer dashboard now reflects approved response from database")

        # 8. Administrator updates status to In Progress, then Resolved
        update_ticket_status(ticket_id, "In Progress", "Technical Operations")
        ticket_in_progress = get_ticket(ticket_id)
        assert ticket_in_progress["ticket_status"] == "In Progress"
        print(f"  [PASS] Admin changed status to In Progress")

        update_ticket_status(ticket_id, "Resolved", "Technical Operations")
        ticket_resolved = get_ticket(ticket_id)
        assert ticket_resolved["ticket_status"] == "Resolved"
        assert ticket_resolved["resolved_at"] is not None, "resolved_at timestamp should be set upon resolution"
        print(f"  [PASS] Admin marked ticket as Resolved (resolved_at timestamp set: {ticket_resolved['resolved_at']})")

        # 9. Verify consistency between customer and admin view
        final_cust_ticket = next(t for t in get_user_tickets(customer_id) if t["id"] == ticket_id)
        final_admin_ticket = get_ticket(ticket_id)
        assert final_cust_ticket["ticket_status"] == final_admin_ticket["ticket_status"] == "Resolved"
        assert final_cust_ticket["approval_status"] == final_admin_ticket["approval_status"] == "Approved"
        assert final_cust_ticket["resolved_at"] == final_admin_ticket["resolved_at"]
        print(f"  [PASS] Customer and Admin dashboards display 100% consistent state from the database")

    finally:
        # Clean up only the temporary test ticket so database stays at original 15 records
        delete_ticket(ticket_id)
        print(f"  [PASS] Cleaned up test ticket #{ticket_id} to preserve original database records")


if __name__ == "__main__":
    test_customer_and_admin_workflow()
