"""
SupportAI – VoltWay Networks
Customer Support & Ticket Intelligence Platform for EV Charging Networks.
"""

from ev_config import (
    BUSINESS_NAME,
    SAMPLE_STATIONS,
)
import json
import os
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

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

from database import (
    authenticate_user, create_user, get_all_tickets, get_user_tickets,
    save_ticket, update_approval_status, update_ticket_reply, update_ticket_status
)
from llm_service import API_KEY, analyze_ticket
from routing import route_ticket
from theme import apply_theme, style_chart
from cursor_bg import inject_cursor_background

st.set_page_config(
    page_title="VoltWay Networks · SupportAI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Google Antigravity visual theme and cursor background animation
inject_cursor_background()
apply_theme()


REMEMBERED_LOGIN_FILE = Path(__file__).parent / ".remembered_login.json"


def load_remembered_login():
    """Load previously saved login credentials if remembered on this device."""
    if REMEMBERED_LOGIN_FILE.exists():
        try:
            with open(REMEMBERED_LOGIN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                email = str(data.get("email", "")).strip()
                password = str(data.get("password", ""))
                remember = bool(data.get("remember", True))
                return email, password, remember
        except Exception:
            pass
    return "", "", True


def save_remembered_login(email, password, remember=True):
    """Store or remove remembered login credentials on this device."""
    try:
        if remember and email:
            data = {"email": email.strip(), "password": password, "remember": True}
            with open(REMEMBERED_LOGIN_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
        else:
            clear_remembered_login()
    except Exception as exc:
        print("Failed to save login info:", exc)


def clear_remembered_login():
    """Remove stored login credentials from disk."""
    try:
        if REMEMBERED_LOGIN_FILE.exists():
            REMEMBERED_LOGIN_FILE.unlink()
    except Exception:
        pass


def login_screen():
    saved_email, saved_password, saved_remember = load_remembered_login()

    # Pre-populate session state if not already set in this session
    if "login_email_val" not in st.session_state:
        st.session_state["login_email_val"] = saved_email
    if "login_password_val" not in st.session_state:
        st.session_state["login_password_val"] = saved_password

    # Brand banner - Antigravity Glass Card with subtle gradient accent
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.92); padding: 24px 32px; border-radius: 16px; border: 1px solid #E3E7EF; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); margin-bottom: 28px; backdrop-filter: blur(10px);">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="background: linear-gradient(135deg, rgba(66, 133, 244, 0.12), rgba(245, 56, 160, 0.12)); border: 1px solid rgba(66, 133, 244, 0.25); border-radius: 999px; width: 46px; height: 46px; display: flex; align-items: center; justify-content: center; font-size: 22px;">⚡</div>
            <div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #1F1F1F; letter-spacing: -0.02em;">VOLTWAY <span class="ag-gradient-text">NETWORKS</span></div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #1A73E8; letter-spacing: 0.06em; text-transform: uppercase;">SupportAI · Customer Support & Network Operations Platform</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.subheader("Public EV Charging Support Hub")
        st.write(
            "VoltWay Networks operates high-reliability electric vehicle charging infrastructure "
            "across Pune, Mumbai, and Nashik. SupportAI provides rapid AI-assisted triage, "
            "automatic engineering team dispatch, and real-time resolution tracking."
        )

        st.markdown("""
        <div style="background: rgba(248, 249, 252, 0.85); border: 1px solid #E3E7EF; border-radius: 14px; padding: 18px 22px; margin-top: 16px; backdrop-filter: blur(8px);">
            <div style="font-weight: 700; color: #1A73E8; margin-bottom: 8px; font-size: 0.95rem;">⚡ Platform Capabilities</div>
            <ul style="margin: 0; padding-left: 20px; color: #5F6368; font-size: 0.88rem; line-height: 1.7;">
                <li><strong style="color: #1F1F1F;">Automated Triage:</strong> Fast charging failure, connector errors & payment mismatch diagnosis.</li>
                <li><strong style="color: #1F1F1F;">Safety Prioritization:</strong> Immediate escalation for thermal, cable, or electrical hazards.</li>
                <li><strong style="color: #1F1F1F;">Human-in-the-Loop:</strong> All customer responses verified and approved by operations engineers.</li>
                <li><strong style="color: #1F1F1F;">SLA Assurance:</strong> Dedicated 2h/4h/8h resolution targets by department.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Customers can create an account. Administrator accounts are pre-provisioned via secure environment credentials.")

    with right:
        login_tab, register_tab = st.tabs(["Sign in", "Create customer account"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    value=st.session_state.get("login_email_val", saved_email),
                    key="login_email"
                )
                password = st.text_input(
                    "Password",
                    value=st.session_state.get("login_password_val", saved_password),
                    type="password",
                    key="login_password"
                )
                remember = st.checkbox(
                    "Remember my login info for future sign-ins",
                    value=saved_remember,
                    key="remember_login_checkbox"
                )
                submitted = st.form_submit_button("Sign in to VoltWay", type="primary", use_container_width=True)

            if submitted:
                user = authenticate_user(email, password)
                if user:
                    if remember:
                        save_remembered_login(email, password, remember=True)
                    else:
                        clear_remembered_login()
                    st.session_state["user"] = user
                    st.rerun()
                st.error("Email or password is incorrect.")

            if saved_email:
                sub_c1, sub_c2 = st.columns([1.6, 1])
                with sub_c1:
                    st.caption(f"🔒 Login info saved for `{saved_email}`")
                with sub_c2:
                    if st.button("Forget saved info", key="btn_clear_login", use_container_width=True):
                        clear_remembered_login()
                        st.session_state["login_email_val"] = ""
                        st.session_state["login_password_val"] = ""
                        st.session_state.pop("login_email", None)
                        st.session_state.pop("login_password", None)
                        st.rerun()

        with register_tab:
            with st.form("register_form"):
                name = st.text_input("Full name", key="register_name")
                new_email = st.text_input("Email address", key="register_email")
                new_password = st.text_input("Password (minimum 8 characters)", type="password", key="register_password")
                confirm = st.text_input("Confirm password", type="password", key="register_confirm")
                created = st.form_submit_button("Register Customer Account", type="primary", use_container_width=True)
            if created:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        create_user(name, new_email, new_password, "user")
                        save_remembered_login(new_email, new_password, remember=True)
                        st.session_state["login_email_val"] = new_email
                        st.session_state["login_password_val"] = new_password
                        st.success("Account created and login info stored. Please switch to Sign in.")
                    except ValueError as exc:
                        st.error(str(exc))


def ticket_card(ticket, admin=False, key_suffix="default"):
    ticket_id = ticket["id"]
    prefix = f"ticket_{ticket_id}_{key_suffix}"

    status = ticket.get("ticket_status", "Open")
    urgency = ticket.get("urgency", "Medium")
    escalation = ticket.get("escalation_status", "Normal")
    mode = "Live AI" if ticket.get("analysis_mode") == "Gemini AI" else "Rule-Based Fallback"

    # Color tokens for badges matching Google Antigravity design system
    status_colors = {
        "Open": ("#1A73E8", "rgba(26, 115, 232, 0.10)"),
        "In Progress": ("#B06000", "rgba(251, 188, 4, 0.16)"),
        "Awaiting Customer": ("#A142F4", "rgba(161, 66, 244, 0.12)"),
        "Resolved": ("#1E8E3E", "rgba(52, 168, 83, 0.12)"),
        "Closed": ("#5F6368", "rgba(95, 99, 104, 0.10)"),
    }
    status_fg, status_bg = status_colors.get(status, ("#1A73E8", "rgba(26, 115, 232, 0.10)"))

    urgency_colors = {
        "Critical": ("#D93025", "rgba(234, 67, 53, 0.12)"),
        "High": ("#E37400", "rgba(250, 123, 23, 0.12)"),
        "Medium": ("#1A73E8", "rgba(26, 115, 232, 0.10)"),
        "Low": ("#1E8E3E", "rgba(52, 168, 83, 0.12)"),
    }
    urgency_fg, urgency_bg = urgency_colors.get(urgency, ("#1A73E8", "rgba(26, 115, 232, 0.10)"))

    # Check for safety terms
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

    card_border = "#EA4335" if is_safety_incident or escalation == "Escalated" else "#E3E7EF"

    with st.container(border=True):
        # Header banner inside card
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid #EEF2F6; padding-bottom: 12px; margin-bottom: 14px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #1F1F1F;">
                <span style="color: #1A73E8; font-family: 'JetBrains Mono', monospace; font-weight: 700;">#{ticket_id}</span> · {ticket.get('subject') or 'Support request'}
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span style="background: {status_bg}; color: {status_fg}; border: 1px solid {status_fg}; padding: 3px 12px; border-radius: 999px; font-size: 0.76rem; font-weight: 700; text-transform: uppercase;">
                    ● {status}
                </span>
                <span style="background: {urgency_bg}; color: {urgency_fg}; border: 1px solid {urgency_fg}; padding: 3px 12px; border-radius: 999px; font-size: 0.76rem; font-weight: 700; text-transform: uppercase;">
                    {urgency}
                </span>
                <span style="background: #F8F9FC; color: #5F6368; border: 1px solid #E3E7EF; padding: 3px 12px; border-radius: 999px; font-size: 0.76rem; font-weight: 600;">
                    {mode}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        a, b, c, d = st.columns(4)
        a.metric("Category", ticket.get("category", "—"))
        b.metric("Urgency", ticket.get("urgency", "—"))
        c.metric("Status", ticket.get("ticket_status", "Open"))
        d.metric("Assigned team", ticket.get("assigned_team", "General Support"))

        st.markdown(f"""
        <div style="background: #F8F9FC; border: 1px solid #E3E7EF; border-radius: 12px; padding: 14px 18px; margin: 12px 0;">
            <div style="font-size: 0.78rem; font-weight: 700; color: #5F6368; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Customer Reported Issue</div>
            <div style="color: #1F1F1F; font-size: 0.92rem; line-height: 1.6;">{ticket.get('ticket_text', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(66, 133, 244, 0.05), rgba(161, 66, 244, 0.05)); border: 1px solid rgba(66, 133, 244, 0.20); border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-size: 0.78rem; font-weight: 700; color: #1A73E8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">⚡ AI Operational Summary</div>
            <div style="color: #3C4043; font-size: 0.90rem; line-height: 1.6;">{ticket.get('summary', '') or 'Summary pending analysis.'}</div>
        </div>
        """, unsafe_allow_html=True)

        # EV-specific operational details captured at ticket submission
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
            with st.expander("⚡ EV Charging Technical Details", expanded=admin):
                detail_cols = st.columns(2)
                for index, (label, value) in enumerate(available_station_fields):
                    detail_cols[index % 2].markdown(f"**{label}:** `{value}`")

        # Safety & Escalation alerts
        if is_safety_incident:
            st.error(
                "🚨 SAFETY INCIDENT — Potential electrical/thermal hazard detected. "
                "Prioritize immediate human review. Customer advised to move away from equipment."
            )

        if escalation == "Escalated":
            st.error(f"⚡ Escalated: {ticket.get('escalation_reason') or 'Human review required.'}")
        elif escalation == "Priority Review":
            st.warning("⚠️ Priority Review: Expedited investigation queue active.")

        # Support Response Presentation
        if admin:
            st.markdown("""
            <div style="font-size: 0.85rem; font-weight: 700; color: #1A73E8; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 14px; margin-bottom: 6px;">
                Suggested AI Customer Reply
            </div>
            """, unsafe_allow_html=True)
            st.info(ticket.get("draft_reply", "A support agent will review your request."))
        elif ticket.get("approval_status") == "Approved":
            st.markdown("""
            <div style="background: rgba(52, 168, 83, 0.06); border: 1px solid rgba(52, 168, 83, 0.35); border-radius: 12px; padding: 16px 20px; margin: 12px 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="color: #1E8E3E; font-size: 1.1rem; font-weight: 700;">✓</span>
                    <strong style="color: #1E8E3E; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.06em;">Official VoltWay Support Response</strong>
                </div>
                <div style="color: #1F1F1F; font-size: 0.92rem; line-height: 1.6;">""" + str(ticket.get("draft_reply", "")) + """</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Your ticket has been received. An operations specialist is reviewing the response.")

        # Admin Actions
        if admin:
            with st.expander("🛠️ Administrator Operations Controls", expanded=False):
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
                st.caption(f"Reply approval: **{ticket.get('approval_status', 'Pending')}** · SLA Due: `{ticket.get('sla_due_at', '—')}`")
                x, y, z = st.columns(3)
                if x.button("💾 Save response", key=f"{prefix}_save", use_container_width=True):
                    try:
                        update_ticket_reply(ticket_id, reply)
                        st.success("Response saved.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                if y.button("✓ Approve response", key=f"{prefix}_approve", type="primary", use_container_width=True):
                    try:
                        update_ticket_reply(ticket_id, reply)
                        update_approval_status(ticket_id, "Approved")
                        st.success("Response approved.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                if z.button("⚡ Update ticket", key=f"{prefix}_update", use_container_width=True):
                    try:
                        update_ticket_status(ticket_id, status, team)
                        st.success("Ticket updated.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
        else:
            st.caption(f"Submitted: {ticket.get('created_at', '—')} · Review status: {ticket.get('approval_status', 'Pending')}")


def customer_dashboard(user):
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.92); padding: 22px 28px; border-radius: 16px; border: 1px solid #E3E7EF; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); margin-bottom: 24px; backdrop-filter: blur(10px);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1F1F1F;">Welcome back, {user['name']} 👋</div>
                <div style="color: #5F6368; font-size: 0.9rem;">VoltWay Customer Support Hub · Public EV Charging Assistance</div>
            </div>
            <div style="background: rgba(52, 168, 83, 0.10); border: 1px solid #34A853; color: #1E8E3E; padding: 6px 16px; border-radius: 999px; font-size: 0.8rem; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 10px;">●</span> NETWORK OPERATIONAL
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tickets = get_user_tickets(user["id"])
    open_count = sum(t.get("ticket_status") in ("Open", "In Progress", "Awaiting Customer") for t in tickets)
    resolved = sum(t.get("ticket_status") in ("Resolved", "Closed") for t in tickets)

    m1, m2, m3 = st.columns(3)
    m1.metric("My Submitted Tickets", len(tickets))
    m2.metric("Active / Being Handled", open_count)
    m3.metric("Resolved Tickets", resolved)

    submit_tab, history_tab = st.tabs(["⚡ Report an EV Charging Issue", "📋 My Ticket History"])

    with submit_tab:
        st.subheader("Report an EV charging issue")
        st.caption("Submit charging session errors, payment deductions, connector locks, or station availability issues.")

        station_options = {
            f"{s['station_id']} | {s['station_name']} ({s['city']})":
            s
            for s in SAMPLE_STATIONS
        }

        with st.form("customer_ticket_form"):
            station_label = st.selectbox(
                "Select charging station",
                list(station_options.keys())
            )

            station = station_options[station_label]

            # EV Station preview card
            is_dc = "DC" in station["charger_type"]
            badge_color = "#1A73E8" if is_dc else "#1E8E3E"
            badge_bg = "rgba(26, 115, 232, 0.10)" if is_dc else "rgba(52, 168, 83, 0.10)"
            status_color = "#1E8E3E" if station["station_status"] == "Operational" else "#E37400"

            st.markdown(f"""
            <div style="background: #F8F9FC; border: 1px solid #E3E7EF; border-radius: 12px; padding: 14px 18px; margin: 10px 0 16px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="color: #1F1F1F; font-weight: 700; font-size: 0.95rem;">⚡ {station['station_name']}</div>
                    <div style="color: #5F6368; font-size: 0.82rem;">{station['area']}, {station['city']} · Station ID: <code style="color: #1A73E8; background: #E8F0FE; padding: 2px 6px; border-radius: 4px;">{station['station_id']}</code></div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; padding: 3px 12px; border-radius: 999px; font-size: 0.76rem; font-weight: 700;">
                        {station['charger_type']}
                    </span>
                    <span style="background: #FFFFFF; color: #1F1F1F; border: 1px solid #E3E7EF; padding: 3px 12px; border-radius: 999px; font-size: 0.76rem; font-weight: 700;">
                        ⚡ {station['power_kw']} kW
                    </span>
                    <span style="color: {status_color}; font-size: 0.76rem; font-weight: 700;">
                        ● {station['station_status']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            subject = st.text_input(
                "Complaint subject",
                placeholder="e.g. EV charger connector error during DC fast charging"
            )

            ticket_text = st.text_area(
                "Describe your problem",
                height=140,
                placeholder="Explain what happened during your charging session (e.g., error codes, cable connection attempts, billing issues)..."
            )

            col1, col2 = st.columns(2)
            with col1:
                transaction_id = st.text_input(
                    "Transaction ID (optional)",
                    placeholder="e.g. TXN-102948"
                )
            with col2:
                session_id = st.text_input(
                    "Charging session ID (optional)",
                    placeholder="e.g. SES-99482"
                )

            vehicle_model = st.text_input(
                "Vehicle model (optional)",
                placeholder="e.g. Tata Nexon EV, MG ZS EV, Mahindra XUV400"
            )

            submit = st.form_submit_button(
                "⚡ Submit EV Charging Complaint",
                type="primary",
                use_container_width=True
            )

        if submit:
            if not subject.strip() or not ticket_text.strip():
                st.warning("Please enter a subject and complaint description.")
            else:
                try:
                    with st.spinner("Analyzing your EV support complaint with SupportAI..."):
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

                    st.success(f"✓ Your complaint has been submitted. Ticket Reference: #{ticket_id}")

                    if result.get("analysis_mode") == "Rule-Based Fallback":
                        st.info("ℹ️ Triage performed via VoltWay deterministic rule engine.")

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
            st.info("You haven't submitted any tickets yet. Use the 'Report an EV Charging Issue' tab above.")


def admin_dashboard(user):
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.92); padding: 22px 28px; border-radius: 16px; border: 1px solid #E3E7EF; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); margin-bottom: 24px; backdrop-filter: blur(10px);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1F1F1F;">⚡ Network Operations Center (NOC)</div>
                <div style="color: #5F6368; font-size: 0.9rem;">VoltWay Networks SupportAI Control Panel · Operator: <strong style="color: #1A73E8;">{user['name']}</strong></div>
            </div>
            <div style="background: rgba(26, 115, 232, 0.10); border: 1px solid #1A73E8; color: #1A73E8; padding: 6px 16px; border-radius: 999px; font-size: 0.8rem; font-weight: 700;">
                ⚡ OPERATIONS LIVE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tickets = get_all_tickets()
    pending = sum(t.get("approval_status") == "Pending" for t in tickets)
    escalated = sum(t.get("escalation_status") == "Escalated" for t in tickets)
    active = sum(t.get("ticket_status") in ("Open", "In Progress", "Awaiting Customer") for t in tickets)
    resolved = sum(t.get("ticket_status") in ("Resolved", "Closed") for t in tickets)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Tickets", len(tickets))
    k2.metric("Awaiting Approval", pending)
    k3.metric("Escalated Incidents", escalated)
    k4.metric("Active Tickets", active)
    k5.metric("Resolved Tickets", resolved)

    overview_tab, queue_tab, analytics_tab = st.tabs([
        "⚡ Live Overview",
        "📋 Ticket Queue & Triage",
        "📊 Network Analytics & SLA"
    ])

    with overview_tab:
        st.subheader("Latest customer requests requiring triage")
        if tickets:
            for ticket in tickets[:5]:
                ticket_card(ticket, admin=True, key_suffix="admin_overview")
        else:
            st.info("No tickets have been submitted.")

    with queue_tab:
        st.subheader("All customer tickets")
        if tickets:
            f1, f2 = st.columns(2)
            urgency_filter = f1.selectbox("Filter by urgency", ["All", "Critical", "High", "Medium", "Low"], key="queue_urgency")
            status_filter = f2.selectbox("Filter by status", ["All", "Open", "In Progress", "Awaiting Customer", "Resolved", "Closed"], key="queue_status")

            filtered = tickets
            if urgency_filter != "All":
                filtered = [t for t in filtered if t.get("urgency") == urgency_filter]
            if status_filter != "All":
                filtered = [t for t in filtered if t.get("ticket_status") == status_filter]

            if filtered:
                st.caption(f"Showing **{len(filtered)}** of **{len(tickets)}** tickets")
                for ticket in filtered:
                    ticket_card(ticket, admin=True, key_suffix="admin_queue")
            else:
                st.info("No tickets match the selected filters.")
        else:
            st.info("Ticket queue is empty.")

    with analytics_tab:
        st.subheader("VoltWay Network Operations Analytics")
        st.caption("Operational overview of customer complaints, department workload, station trends and SLA performance.")

        if not tickets:
            st.info("Analytics will appear when customers submit tickets.")
        else:
            df = pd.DataFrame(tickets).copy()

            for date_col in ("created_at", "sla_due_at", "resolved_at"):
                if date_col not in df.columns:
                    df[date_col] = pd.NaT
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

            now = pd.Timestamp.now()
            active_mask = df["ticket_status"].fillna("Open").isin(["Open", "In Progress", "Awaiting Customer"])
            overdue_mask = active_mask & df["sla_due_at"].notna() & (df["sla_due_at"] < now)
            resolved_mask = df["ticket_status"].fillna("").isin(["Resolved", "Closed"])
            measurable_resolved = resolved_mask & df["resolved_at"].notna() & df["sla_due_at"].notna()

            sla_total = int(measurable_resolved.sum())
            sla_met = int((measurable_resolved & (df["resolved_at"] <= df["sla_due_at"])).sum())
            sla_rate = (sla_met / sla_total * 100) if sla_total else None

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

            total_p = len(view_df)
            active_p = int(view_df["ticket_status"].fillna("Open").isin(["Open", "In Progress", "Awaiting Customer"]).sum())
            overdue_p = int((view_df["ticket_status"].fillna("Open").isin(["Open", "In Progress", "Awaiting Customer"]) & view_df["sla_due_at"].notna() & (view_df["sla_due_at"] < now)).sum())
            escalated_p = int((view_df["escalation_status"] == "Escalated").sum())

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Period Tickets", total_p)
            c2.metric("Active Tickets", active_p)
            c3.metric("Overdue SLA", overdue_p, delta="Needs action" if overdue_p else None, delta_color="inverse")
            c4.metric("Escalated", escalated_p)
            c5.metric("Resolution SLA Met", f"{sla_rate:.1f}%" if sla_rate is not None else "—")

            st.divider()
            st.markdown("### Ticket volume & issue patterns")
            chart1, chart2 = st.columns(2)

            with chart1:
                trend_df = view_df.dropna(subset=["created_at"]).copy()
                if not trend_df.empty:
                    trend_df["Month"] = trend_df["created_at"].dt.to_period("M").astype(str)
                    monthly = trend_df.groupby("Month").size().reset_index(name="Tickets")
                    fig1 = px.line(
                        monthly, x="Month", y="Tickets", markers=True,
                        title="Monthly Ticket Volume",
                        color_discrete_sequence=["#1A73E8"]
                    )
                    st.plotly_chart(style_chart(fig1), use_container_width=True)
                else:
                    st.info("No dated tickets in this reporting period.")

            with chart2:
                category_counts = (
                    view_df["category"].fillna("Unclassified")
                    .value_counts().rename_axis("Category")
                    .reset_index(name="Tickets")
                )
                if not category_counts.empty:
                    fig2 = px.pie(
                        category_counts, names="Category", values="Tickets",
                        title="Complaints by Issue Category", hole=0.45,
                        color_discrete_sequence=["#1A73E8", "#A142F4", "#F538A0", "#34A853", "#FBBC04", "#4285F4", "#EA4335"]
                    )
                    st.plotly_chart(style_chart(fig2), use_container_width=True)

            st.markdown("### Charging network station performance")
            station_col, city_col = st.columns(2)
            with station_col:
                station_data = view_df.copy()
                station_data["station_name"] = station_data["station_name"].fillna("Station not recorded")
                station_counts = (
                    station_data.groupby("station_name").size()
                    .reset_index(name="Tickets").sort_values("Tickets", ascending=False)
                )
                fig3 = px.bar(
                    station_counts, x="station_name", y="Tickets",
                    title="Complaints by Charging Station",
                    color_discrete_sequence=["#1A73E8"]
                )
                st.plotly_chart(style_chart(fig3), use_container_width=True)

            with city_col:
                city_data = view_df.copy()
                city_data["station_city"] = city_data["station_city"].fillna("City not recorded")
                city_counts = (
                    city_data.groupby("station_city").size()
                    .reset_index(name="Tickets").sort_values("Tickets", ascending=False)
                )
                fig4 = px.bar(
                    city_counts, x="station_city", y="Tickets",
                    title="Complaints by City",
                    color_discrete_sequence=["#34A853"]
                )
                st.plotly_chart(style_chart(fig4), use_container_width=True)

            st.markdown("### Department workload & urgency distribution")
            team_col, urgency_col = st.columns(2)
            with team_col:
                team_data = view_df.copy()
                team_data["assigned_team"] = team_data["assigned_team"].fillna("Unassigned")
                team_counts = (
                    team_data.groupby("assigned_team").size()
                    .reset_index(name="Tickets").sort_values("Tickets", ascending=False)
                )
                fig5 = px.bar(
                    team_counts, x="assigned_team", y="Tickets",
                    title="Workload by Support Department",
                    color_discrete_sequence=["#A142F4"]
                )
                st.plotly_chart(style_chart(fig5), use_container_width=True)

            with urgency_col:
                urgency_order = ["Low", "Medium", "High", "Critical"]
                urgency_counts = (
                    view_df["urgency"].fillna("Unclassified").value_counts()
                    .rename_axis("Urgency").reset_index(name="Tickets")
                )
                fig6 = px.bar(
                    urgency_counts, x="Urgency", y="Tickets",
                    title="Tickets by Urgency",
                    category_orders={"Urgency": urgency_order},
                    color_discrete_sequence=["#FA7B17"]
                )
                st.plotly_chart(style_chart(fig6), use_container_width=True)

            st.markdown("### SLA monitoring")
            sla_left, sla_right = st.columns(2)
            with sla_left:
                if overdue_p:
                    st.error(f"🚨 {overdue_p} active ticket(s) are past their SLA deadline.")
                else:
                    st.success("✓ No active tickets are currently past their recorded SLA deadline.")

                overdue_rows = view_df[
                    view_df["ticket_status"].fillna("Open").isin(["Open", "In Progress", "Awaiting Customer"])
                    & view_df["sla_due_at"].notna()
                    & (view_df["sla_due_at"] < now)
                ].copy()
                if not overdue_rows.empty:
                    st.markdown("**Overdue Ticket Queue**")
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
                    help="Calculated for resolved/closed tickets with both a recorded SLA deadline and resolution timestamp."
                )
                if sla_total:
                    sla_chart = pd.DataFrame({
                        "SLA result": ["Within SLA", "Beyond SLA"],
                        "Tickets": [sla_met, sla_total - sla_met],
                    })
                    fig7 = px.pie(
                        sla_chart, names="SLA result", values="Tickets",
                        title="Resolution SLA Compliance", hole=0.45,
                        color_discrete_sequence=["#34A853", "#EA4335"]
                    )
                    st.plotly_chart(style_chart(fig7), use_container_width=True)

            resolved_times = view_df[
                view_df["resolved_at"].notna() & view_df["created_at"].notna()
            ].copy()
            if not resolved_times.empty:
                resolved_times["Resolution hours"] = (
                    resolved_times["resolved_at"] - resolved_times["created_at"]
                ).dt.total_seconds() / 3600
                avg_hours = resolved_times["Resolution hours"].clip(lower=0).mean()
                st.metric("Average Recorded Resolution Time", f"{avg_hours:.1f} hours")

            st.markdown("### Ticket-level operations export")
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
                "📥 Download Operations Report (CSV)",
                data=csv_data,
                file_name="voltway_operations_report.csv",
                mime="text/csv",
            )


def main():
    import database

    if "user" not in st.session_state:
        login_screen()
        return

    user = st.session_state["user"]
    if user.get("role") not in ("admin", "user"):
        st.session_state.pop("user", None)
        st.error("Invalid account role. Please sign in again.")
        st.rerun()

    is_admin = user["role"] == "admin"

    with st.sidebar:
        # Branding
        st.markdown("""
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #E3E7EF; margin-bottom: 16px;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #1F1F1F; letter-spacing: -0.02em; display: flex; align-items: center; gap: 8px;">
                <span>⚡</span> VOLTWAY <span class="ag-gradient-text" style="font-size: 1.15rem;">AI</span>
            </div>
            <div style="font-size: 0.72rem; font-weight: 700; color: #5F6368; letter-spacing: 0.10em; text-transform: uppercase;">
                SUPPORTAI · EV CHARGING OPS
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Profile card
        role_label = "⚡ NOC Administrator" if is_admin else "🚘 EV Driver Account"
        role_badge_color = "#1A73E8" if is_admin else "#1E8E3E"
        role_badge_bg = "rgba(26, 115, 232, 0.10)" if is_admin else "rgba(52, 168, 83, 0.10)"

        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #E3E7EF; border-radius: 14px; padding: 14px 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);">
            <div style="font-weight: 700; color: #1F1F1F; font-size: 0.98rem; margin-bottom: 4px;">{user['name']}</div>
            <div style="display: inline-block; background: {role_badge_bg}; color: {role_badge_color}; border: 1px solid {role_badge_color}; border-radius: 999px; padding: 2px 10px; font-size: 0.74rem; font-weight: 700; text-transform: uppercase;">
                {role_label}
            </div>
            <div style="color: #5F6368; font-size: 0.78rem; margin-top: 6px;">{user.get('email', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sign out", key="sidebar_sign_out", use_container_width=True):
            st.session_state.pop("user", None)
            st.rerun()

        st.markdown("<hr style='border-color: #E3E7EF; margin: 18px 0;'>", unsafe_allow_html=True)

        # AI Status Card
        st.markdown("""
        <div style="font-size: 0.78rem; font-weight: 700; color: #5F6368; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
            AI Service Engine
        </div>
        """, unsafe_allow_html=True)
        if API_KEY:
            st.markdown("""
            <div style="background: rgba(52, 168, 83, 0.08); border: 1px solid #34A853; border-radius: 12px; padding: 12px 14px; font-size: 0.80rem; color: #1E8E3E; font-weight: 600;">
                ● Gemini AI Engine Configured<br>
                <span style="color: #5F6368; font-weight: 400; font-size: 0.75rem;">Deterministic fallback standby active</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(251, 188, 4, 0.12); border: 1px solid #FBBC04; border-radius: 12px; padding: 12px 14px; font-size: 0.80rem; color: #B06000; font-weight: 600;">
                ● Internal Fallback Engine Active<br>
                <span style="color: #5F6368; font-weight: 400; font-size: 0.75rem;">Offline EV rule classifier running</span>
            </div>
            """, unsafe_allow_html=True)

        # Database Status Card
        db_is_mongo = getattr(database, "MONGO_CONNECTED", False)
        st.markdown("""
        <div style="font-size: 0.78rem; font-weight: 700; color: #5F6368; text-transform: uppercase; letter-spacing: 0.08em; margin: 14px 0 8px 0;">
            Data Layer
        </div>
        """, unsafe_allow_html=True)
        if db_is_mongo:
            st.markdown("""
            <div style="background: rgba(26, 115, 232, 0.08); border: 1px solid #1A73E8; border-radius: 12px; padding: 12px 14px; font-size: 0.80rem; color: #1A73E8; font-weight: 600;">
                ● MongoDB Atlas (Live Cluster)<br>
                <span style="color: #5F6368; font-weight: 400; font-size: 0.75rem;">Cloud synchronization enabled</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(52, 168, 83, 0.08); border: 1px solid #34A853; border-radius: 12px; padding: 12px 14px; font-size: 0.80rem; color: #1E8E3E; font-weight: 600;">
                ● High-Performance Storage Active<br>
                <span style="color: #5F6368; font-weight: 400; font-size: 0.75rem;">15 pre-loaded benchmark tickets</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top: 24px; padding-top: 14px; border-top: 1px solid #E3E7EF; font-size: 0.72rem; color: #5F6368; text-align: center;">
            VoltWay Networks · Version 2.2<br>Google Antigravity Design System
        </div>
        """, unsafe_allow_html=True)

    try:
        if user["role"] == "admin":
            admin_dashboard(user)
        else:
            customer_dashboard(user)
    except Exception as exc:
        st.error("Something went wrong while loading the dashboard. Check the terminal.")
        print("Dashboard error:", type(exc).__name__, str(exc))


if __name__ == "__main__":
    main()
