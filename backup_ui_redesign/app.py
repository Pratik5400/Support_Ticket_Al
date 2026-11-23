
from ev_config import (
    BUSINESS_NAME,
    SAMPLE_STATIONS,
)
import pandas as pd




import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from database import (
    authenticate_user, create_user, get_all_tickets, get_user_tickets,
    save_ticket, update_approval_status, update_ticket_reply, update_ticket_status
)
from llm_service import API_KEY, analyze_ticket
from routing import route_ticket

st.set_page_config(page_title="SupportAI", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {font-family:Inter,sans-serif!important;color:#171a2b!important}
.stApp {background:#f4f6fb!important}
[data-testid="stHeader"],[data-testid="stToolbar"] {background:#fff!important}
.block-container {padding-top:2rem!important;max-width:1400px!important}
h1,h2,h3,h4,p,label,.stMarkdown,.stCaption,[data-testid="stWidgetLabel"] {color:#171a2b!important}
[data-testid="stSidebar"] {background:#fff!important}
[data-testid="stSidebar"] * {color:#171a2b}
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div {
 background:#fff!important;color:#171a2b!important;border:1px solid #d9deeb!important;border-radius:10px!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder {color:#9ca3af!important}
.stTabs [data-baseweb="tab-list"] {background:#e9ebf5!important;border-radius:12px!important}
.stTabs [data-baseweb="tab"] {color:#4b5563!important}
.stTabs [aria-selected="true"] {color:#4f46e5!important;background:#fff!important}
.stButton>button,.stFormSubmitButton>button {
 background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:#fff!important;border:0!important;
 border-radius:10px!important;font-weight:600!important;min-height:42px}
[data-testid="stMetric"] {background:#fff!important;padding:18px!important;border-radius:14px!important;border:1px solid #edf0f7!important}
[data-testid="stMetric"] label,[data-testid="stMetricValue"] {color:#171a2b!important}
[data-testid="stAlert"] {border-radius:10px!important}
hr {border-color:#e5e7eb!important}
</style>
""", unsafe_allow_html=True)


def login_screen():
    st.title("✦ SupportAI")
    st.caption("Customer Support & Ticket Intelligence Platform")
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Welcome")
        st.write("Submit support requests, track progress, and receive guided responses.")
        st.info("Customers can create an account. Administrator accounts are provisioned separately.")
    with right:
        login_tab, register_tab = st.tabs(["Sign in", "Create customer account"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if submitted:
                user = authenticate_user(email, password)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                st.error("Email or password is incorrect.")
        with register_tab:
            with st.form("register_form"):
                name = st.text_input("Full name", key="register_name")
                new_email = st.text_input("Email address", key="register_email")
                new_password = st.text_input("Password (minimum 8 characters)", type="password", key="register_password")
                confirm = st.text_input("Confirm password", type="password", key="register_confirm")
                created = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if created:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        create_user(name, new_email, new_password, "user")
                        st.success("Account created. Please sign in.")
                    except ValueError as exc:
                        st.error(str(exc))


def ticket_card(ticket, admin=False, key_suffix="default"):
    ticket_id = ticket["id"]
    # Every interactive key is unique across ticket ID AND dashboard section.
    prefix = f"ticket_{ticket_id}_{key_suffix}"
    with st.container(border=True):
        st.markdown(f"### Ticket #{ticket_id} · {ticket.get('subject') or 'Support request'}")
        a, b, c, d = st.columns(4)
        a.metric("Category", ticket.get("category", "—"))
        b.metric("Urgency", ticket.get("urgency", "—"))
        c.metric("Status", ticket.get("ticket_status", "Open"))
        d.metric("AI mode", "Gemini" if ticket.get("analysis_mode") == "Gemini AI" else "Fallback")
        st.write("**Issue:**", ticket.get("ticket_text", ""))
        st.write("**Summary:**", ticket.get("summary", ""))
        st.write("**Assigned team:**", ticket.get("assigned_team", "General Support"))

        # EV-specific operational details captured at ticket submission.
        station_fields = [
            ("Station ID", ticket.get("station_id")),
            ("Charging station", ticket.get("station_name")),
            ("City", ticket.get("station_city")),
            ("Transaction ID", ticket.get("transaction_id")),
            ("Charging session ID", ticket.get("session_id")),
            ("Vehicle model", ticket.get("vehicle_model")),
        ]
        available_station_fields = [(label, value) for label, value in station_fields if value]
        if available_station_fields:
            with st.expander("EV complaint details", expanded=admin):
                detail_cols = st.columns(2)
                for index, (label, value) in enumerate(available_station_fields):
                    detail_cols[index % 2].markdown(f"**{label}:** {value}")

        # Highlight safety-related incidents even if the model category is imperfect.
        safety_terms = (
            "smoke", "fire", "burning", "sparking", "electric shock",
            "overheat", "overheating", "explosion", "short circuit"
        )
        ticket_content = " ".join([
            str(ticket.get("subject", "")),
            str(ticket.get("ticket_text", "")),
            str(ticket.get("category", "")),
        ]).lower()
        is_safety_incident = (
            "safety" in str(ticket.get("category", "")).lower()
            or any(term in ticket_content for term in safety_terms)
        )
        if is_safety_incident:
            st.error(
                "SAFETY INCIDENT — Prioritize immediate human review. "
                "If there is active danger, follow the operator's emergency procedure."
            )

        escalation = ticket.get("escalation_status", "Normal")
        if escalation == "Escalated":
            st.error(f"Escalated: {ticket.get('escalation_reason') or 'Human review required.'}")
        elif escalation == "Priority Review":
            st.warning("Priority review required.")

        if admin:
            st.write("**Suggested response:**")
            st.info(ticket.get("draft_reply", "A support agent will review your request."))
        elif ticket.get("approval_status") == "Approved":
            st.write("**Support response:**")
            st.info(ticket.get("draft_reply", ""))
        else:
            st.info("Your ticket has been received. A support agent is reviewing the suggested response.")

        if admin:
            with st.expander("Admin actions", expanded=False):
                reply = st.text_area("Edit response", value=ticket.get("draft_reply", ""),
                                     key=f"{prefix}_reply", height=130)
                teams = [
                    "Payment Support",
                    "Technical Operations",
                    "Network Operations",
                    "Finance Support",
                    "Account Support",
                    "Safety Operations",
                    "General Support",
                ]
                current_team = ticket.get("assigned_team") or "General Support"
                # Preserve older or custom team values already stored in the database.
                if current_team not in teams:
                    teams.append(current_team)
                team_idx = teams.index(current_team)
                team = st.selectbox(
                    "Assigned team",
                    teams,
                    index=team_idx,
                    key=f"{prefix}_team",
                )
                statuses = ["Open", "In Progress", "Awaiting Customer", "Resolved", "Closed"]
                current_status = ticket.get("ticket_status", "Open")
                status_idx = statuses.index(current_status) if current_status in statuses else 0
                status = st.selectbox("Ticket status", statuses, index=status_idx, key=f"{prefix}_status")
                st.caption(f"Reply approval: {ticket.get('approval_status', 'Pending')}")
                x, y, z = st.columns(3)
                if x.button("Save response", key=f"{prefix}_save"):
                    try:
                        update_ticket_reply(ticket_id, reply)
                        st.success("Response saved.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                if y.button("Approve response", key=f"{prefix}_approve", type="primary"):
                    try:
                        update_ticket_reply(ticket_id, reply)
                        update_approval_status(ticket_id, "Approved")
                        st.success("Response approved.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                if z.button("Update ticket", key=f"{prefix}_update"):
                    try:
                        update_ticket_status(ticket_id, status, team)
                        st.success("Ticket updated.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
        else:
            st.caption(f"Submitted: {ticket.get('created_at', '—')} · Reply review: {ticket.get('approval_status', 'Pending')}")


def customer_dashboard(user):
    st.title(f"Hello, {user['name']} 👋")
    st.caption("Your support centre")
    tickets = get_user_tickets(user["id"])
    open_count = sum(t.get("ticket_status") in ("Open", "In Progress") for t in tickets)
    resolved = sum(t.get("ticket_status") in ("Resolved", "Closed") for t in tickets)
    m1, m2, m3 = st.columns(3)
    m1.metric("My tickets", len(tickets))
    m2.metric("Being handled", open_count)
    m3.metric("Resolved", resolved)

    submit_tab, history_tab = st.tabs(["＋ Submit a ticket", "My ticket history"])

    with submit_tab:
        st.subheader("Report an EV charging issue")

        station_options = {
            f"{s['station_id']} | {s['station_name']} | {s['city']}":
            s
            for s in SAMPLE_STATIONS
        }

        with st.form("customer_ticket_form"):

            subject = st.text_input(
                "Complaint subject",
                placeholder="e.g. Payment deducted but charging did not start"
            )

            station_label = st.selectbox(
                "Select charging station",
                list(station_options.keys())
            )

            station = station_options[station_label]

            st.caption(
                f"Location: {station['area']}, {station['city']} | "
                f"Charger: {station['charger_type']} | "
                f"Power: {station['power_kw']} kW | "
                f"Station status: {station['station_status']}"
            )

            ticket_text = st.text_area(
                "Describe your problem",
                height=150,
                placeholder="Explain what happened during your charging session..."
            )

            col1, col2 = st.columns(2)

            with col1:
                transaction_id = st.text_input(
                    "Transaction ID (optional)"
                )

            with col2:
                session_id = st.text_input(
                    "Charging session ID (optional)"
                )

            vehicle_model = st.text_input(
                "Vehicle model (optional)",
                placeholder="e.g. Tata Nexon EV"
            )

            submit = st.form_submit_button(
                "Submit charging complaint",
                type="primary",
                use_container_width=True
            )

        if submit:

            if not subject.strip() or not ticket_text.strip():
                st.warning("Please enter a subject and complaint description.")

            else:
                try:
                    with st.spinner("Analyzing your EV support complaint..."):
                        full_complaint_text = f"{subject.strip()}\n{ticket_text.strip()}"
                        result = route_ticket(
                            analyze_ticket(full_complaint_text),
                            full_complaint_text
                        )

                        ticket_id = save_ticket(
                            ticket_text.strip(),
                            result,
                            user_id=user["id"],
                            subject=subject.strip(),
                            station_id=station["station_id"],
                            station_name=station["station_name"],
                            station_city=station["city"],
                            transaction_id=transaction_id.strip() or None,
                            session_id=session_id.strip() or None,
                            vehicle_model=vehicle_model.strip() or None,
                        )

                    st.success(
                        f"Your complaint has been submitted. Ticket ID: #{ticket_id}"
                    )

                    if result.get("analysis_mode") == "Rule-Based Fallback":
                        st.warning(
                            "Gemini is unavailable. An internal AI fallback "
                            "engine generated your response."
                        )

                    st.rerun()

                except Exception as exc:
                    st.error("Unable to submit complaint. Check the terminal.")
                    print("EV ticket submission error:", repr(exc))

    with history_tab:
        st.subheader("My submitted tickets")
        if tickets:
            for ticket in tickets:
                ticket_card(ticket, admin=False, key_suffix="customer_history")
        else:
            st.info("You haven't submitted any tickets yet. Use the 'Submit a ticket' tab to report an issue.")



def admin_dashboard(user):
    st.title("Administrator Dashboard")
    st.caption(f"Signed in as {user['name']} · Manage customer support operations")
    tickets = get_all_tickets()
    pending = sum(t.get("approval_status") == "Pending" for t in tickets)
    escalated = sum(t.get("escalation_status") == "Escalated" for t in tickets)
    active = sum(t.get("ticket_status") in ("Open", "In Progress") for t in tickets)
    a, b, c, d = st.columns(4)
    a.metric("Total tickets", len(tickets))
    b.metric("Awaiting approval", pending)
    c.metric("Escalated", escalated)
    d.metric("Active", active)

    overview_tab, queue_tab, analytics_tab = st.tabs(["Overview", "Ticket management", "Analytics"])
    with overview_tab:
        st.subheader("Latest customer requests")
        if tickets:
            for ticket in tickets[:5]:
                ticket_card(ticket, admin=True, key_suffix="admin_overview")
        else:
            st.info("No tickets have been submitted.")

    with queue_tab:
        st.subheader("All customer tickets")
        if tickets:
            f1, f2 = st.columns(2)
            urgency_filter = f1.selectbox("Urgency", ["All", "Critical", "High", "Medium", "Low"], key="queue_urgency")
            status_filter = f2.selectbox("Status", ["All", "Open", "In Progress", "Awaiting Customer", "Resolved", "Closed"], key="queue_status")
            filtered = tickets
            if urgency_filter != "All":
                filtered = [t for t in filtered if t.get("urgency") == urgency_filter]
            if status_filter != "All":
                filtered = [t for t in filtered if t.get("ticket_status") == status_filter]
            if filtered:
                for ticket in filtered:
                    ticket_card(ticket, admin=True, key_suffix="admin_queue")
            else:
                st.info("No tickets match the selected filters.")
        else:
            st.info("Ticket queue is empty.")

    with analytics_tab:
        st.subheader("VoltWay Network Operations Analytics")
        st.caption(
            "Operational view of customer complaints, support workload, station trends "
            "and ticket-resolution SLA performance."
        )

        if not tickets:
            st.info("Analytics will appear when customers submit tickets.")
        else:
            df = pd.DataFrame(tickets).copy()

            # Normalize dates while keeping the analytics resilient to legacy rows.
            for date_col in ("created_at", "sla_due_at", "resolved_at"):
                if date_col not in df.columns:
                    df[date_col] = pd.NaT
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

            now = pd.Timestamp.now()
            active_mask = df["ticket_status"].fillna("Open").isin(["Open", "In Progress"])
            overdue_mask = (
                active_mask
                & df["sla_due_at"].notna()
                & (df["sla_due_at"] < now)
            )
            resolved_mask = df["ticket_status"].fillna("").isin(["Resolved", "Closed"])
            measurable_resolved = (
                resolved_mask
                & df["resolved_at"].notna()
                & df["sla_due_at"].notna()
            )
            sla_total = int(measurable_resolved.sum())
            sla_met = int(
                (
                    measurable_resolved
                    & (df["resolved_at"] <= df["sla_due_at"])
                ).sum()
            )
            sla_rate = (sla_met / sla_total * 100) if sla_total else None

            # Date range selector.
            period = st.selectbox(
                "Reporting period",
                ["All time", "Last 30 days", "Last 90 days"],
                key="ops_analytics_period",
            )
            view_df = df.copy()
            if period != "All time":
                days = 30 if period == "Last 30 days" else 90
                view_df = view_df[
                    view_df["created_at"].notna()
                    & (view_df["created_at"] >= now - pd.Timedelta(days=days))
                ]

            total = len(view_df)
            active = int(view_df["ticket_status"].fillna("Open").isin(["Open", "In Progress"]).sum())
            overdue_view = int(
                (
                    view_df["ticket_status"].fillna("Open").isin(["Open", "In Progress"])
                    & view_df["sla_due_at"].notna()
                    & (view_df["sla_due_at"] < now)
                ).sum()
            )
            escalated_view = int((view_df["escalation_status"] == "Escalated").sum())

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Tickets in period", total)
            k2.metric("Active tickets", active)
            k3.metric("Overdue SLA", overdue_view, delta="Needs attention" if overdue_view else None,
                      delta_color="inverse")
            k4.metric("Escalated", escalated_view)
            k5.metric("Resolution SLA met", f"{sla_rate:.1f}%" if sla_rate is not None else "—",
                      help=f"{sla_met} of {sla_total} resolved tickets have recorded resolution timestamps and SLA deadlines.")

            st.divider()
            st.markdown("### Ticket volume and issue patterns")
            chart1, chart2 = st.columns(2)

            with chart1:
                trend_df = view_df.dropna(subset=["created_at"]).copy()
                if not trend_df.empty:
                    trend_df["Month"] = trend_df["created_at"].dt.to_period("M").astype(str)
                    monthly = trend_df.groupby("Month").size().reset_index(name="Tickets")
                    st.plotly_chart(
                        px.line(monthly, x="Month", y="Tickets", markers=True,
                                title="Monthly ticket volume"),
                        use_container_width=True,
                    )
                else:
                    st.info("No dated tickets in this reporting period.")

            with chart2:
                category_counts = (
                    view_df["category"].fillna("Unclassified")
                    .value_counts().rename_axis("Category")
                    .reset_index(name="Tickets")
                )
                if not category_counts.empty:
                    st.plotly_chart(
                        px.pie(category_counts, names="Category", values="Tickets",
                               title="Complaints by issue category", hole=0.42),
                        use_container_width=True,
                    )

            st.markdown("### Charging network performance")
            station_col, city_col = st.columns(2)
            with station_col:
                station_data = view_df.copy()
                station_data["station_name"] = station_data["station_name"].fillna("Station not recorded")
                station_counts = (
                    station_data.groupby("station_name").size()
                    .reset_index(name="Tickets").sort_values("Tickets", ascending=False)
                )
                st.plotly_chart(
                    px.bar(station_counts, x="station_name", y="Tickets",
                           title="Complaints by charging station"),
                    use_container_width=True,
                )

            with city_col:
                city_data = view_df.copy()
                city_data["station_city"] = city_data["station_city"].fillna("City not recorded")
                city_counts = (
                    city_data.groupby("station_city").size()
                    .reset_index(name="Tickets").sort_values("Tickets", ascending=False)
                )
                st.plotly_chart(
                    px.bar(city_counts, x="station_city", y="Tickets",
                           title="Complaints by city"),
                    use_container_width=True,
                )

            st.markdown("### Support team workload and urgency")
            team_col, urgency_col = st.columns(2)
            with team_col:
                team_data = view_df.copy()
                team_data["assigned_team"] = team_data["assigned_team"].fillna("Unassigned")
                team_counts = (
                    team_data.groupby("assigned_team").size()
                    .reset_index(name="Tickets").sort_values("Tickets", ascending=False)
                )
                st.plotly_chart(
                    px.bar(team_counts, x="assigned_team", y="Tickets",
                           title="Workload by support department"),
                    use_container_width=True,
                )
            with urgency_col:
                urgency_order = ["Low", "Medium", "High", "Critical"]
                urgency_counts = (
                    view_df["urgency"].fillna("Unclassified").value_counts()
                    .rename_axis("Urgency").reset_index(name="Tickets")
                )
                st.plotly_chart(
                    px.bar(urgency_counts, x="Urgency", y="Tickets",
                           title="Tickets by urgency",
                           category_orders={"Urgency": urgency_order}),
                    use_container_width=True,
                )

            st.markdown("### SLA monitoring")
            sla_left, sla_right = st.columns(2)
            with sla_left:
                if overdue_view:
                    st.error(f"{overdue_view} active ticket(s) are past their SLA deadline.")
                else:
                    st.success("No active tickets are currently past their recorded SLA deadline.")

                overdue_rows = view_df[
                    view_df["ticket_status"].fillna("Open").isin(["Open", "In Progress"])
                    & view_df["sla_due_at"].notna()
                    & (view_df["sla_due_at"] < now)
                ].copy()
                if not overdue_rows.empty:
                    st.markdown("**Overdue ticket queue**")
                    overdue_rows["sla_due_at"] = overdue_rows["sla_due_at"].dt.strftime("%d %b %Y, %I:%M %p")
                    overdue_columns = [
                        c for c in ["id", "subject", "station_name", "assigned_team",
                                    "urgency", "sla_due_at"] if c in overdue_rows.columns
                    ]
                    st.dataframe(overdue_rows[overdue_columns], hide_index=True, use_container_width=True)
                else:
                    st.caption("Overdue tickets will appear here when an active ticket passes its SLA deadline.")

            with sla_right:
                st.metric(
                    "Resolved within SLA",
                    f"{sla_rate:.1f}%" if sla_rate is not None else "Not enough data",
                    help="Calculated only for resolved/closed tickets with both a recorded SLA deadline and resolution timestamp.",
                )
                st.caption(
                    f"Measured resolved tickets: {sla_total}. "
                    "Older tickets without a recorded resolution timestamp are excluded."
                )
                if sla_total:
                    sla_chart = pd.DataFrame({
                        "SLA result": ["Within SLA", "Beyond SLA"],
                        "Tickets": [sla_met, sla_total - sla_met],
                    })
                    st.plotly_chart(
                        px.pie(sla_chart, names="SLA result", values="Tickets",
                               title="Resolution SLA outcome", hole=0.45),
                        use_container_width=True,
                    )

            resolved_times = view_df[
                view_df["resolved_at"].notna() & view_df["created_at"].notna()
            ].copy()
            if not resolved_times.empty:
                resolved_times["Resolution hours"] = (
                    resolved_times["resolved_at"] - resolved_times["created_at"]
                ).dt.total_seconds() / 3600
                avg_hours = resolved_times["Resolution hours"].clip(lower=0).mean()
                st.metric("Average recorded resolution time", f"{avg_hours:.1f} hours")

            st.markdown("### Ticket-level operations report")
            report_cols = [
                "id", "subject", "station_id", "station_name", "station_city",
                "transaction_id", "session_id", "category", "urgency",
                "assigned_team", "escalation_status", "ticket_status",
                "sla_target", "sla_due_at", "resolved_at", "analysis_mode", "created_at",
            ]
            report_cols = [column for column in report_cols if column in view_df.columns]
            report_df = view_df[report_cols].copy()
            for date_col in ("sla_due_at", "resolved_at", "created_at"):
                if date_col in report_df.columns:
                    report_df[date_col] = pd.to_datetime(report_df[date_col], errors="coerce").dt.strftime(
                        "%d %b %Y, %I:%M %p"
                    )
            st.dataframe(report_df, use_container_width=True, hide_index=True)

            csv_data = report_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download operations report (CSV)",
                data=csv_data,
                file_name="voltway_operations_report.csv",
                mime="text/csv",
            )


def main():
    if "user" not in st.session_state:
        login_screen()
        return

    user = st.session_state["user"]
    if user.get("role") not in ("admin", "user"):
        st.session_state.pop("user", None)
        st.error("Invalid account role. Please sign in again.")
        st.rerun()

    with st.sidebar:
        st.markdown("## ✦ SupportAI")
        st.caption("Ticket Intelligence Platform")
        st.write(f"**{user['name']}**")
        st.caption("Administrator" if user["role"] == "admin" else "Customer")
        if st.button("Sign out", key="sidebar_sign_out", use_container_width=True):
            st.session_state.pop("user", None)
            st.rerun()
        st.divider()
        st.caption("AI service status")
        if API_KEY:
            st.success("Gemini key configured · internal fallback enabled")
        else:
            st.warning("No Gemini key · internal fallback active")

    try:
        if user["role"] == "admin":
            admin_dashboard(user)
        else:
            customer_dashboard(user)
    except Exception as exc:
        st.error("Something went wrong while loading the dashboard. Check the PyCharm terminal.")
        print("Dashboard error:", type(exc).__name__, str(exc))


if __name__ == "__main__":
    main()
