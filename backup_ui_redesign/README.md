# SupportAI – VoltWay Networks

**SupportAI** is an AI-powered customer support and ticket intelligence platform designed for **VoltWay Networks**, a fictional electric vehicle (EV) charging network operator providing public fast-charging services across Pune, Mumbai, and Nashik.

The system classifies customer complaints, determines urgency, routes tickets to the appropriate support department, applies deterministic SLA deadlines, generates suggested responses via Google Gemini AI (with a resilient local rule-based fallback engine), and manages ticket resolution through a human-in-the-loop administrator workflow.

---

## Business Use Case

VoltWay Networks operates public DC Fast Chargers and AC charging points. EV drivers submit complaints regarding:
- Payment deducted but charging session did not initiate
- Connector / cable errors and physical charger malfunctions
- Charging session interruptions and unexpected shutdowns
- Duplicate transaction deductions
- Account security concerns and fraudulent transaction reports
- General inquiries regarding tariffs, station availability, and network hours

SupportAI automates triage and escalation while ensuring that human operators review and approve every outbound communication and refund/investigation action.

---

## System Architecture & Technologies

- **Frontend & UI**: [Streamlit](https://streamlit.io/) with custom responsive styling and role-based views.
- **Backend Database**: [SQLite](https://www.sqlite.org/) (`support_tickets.db`) with schema migrations for EV operational fields and SLA tracking.
- **AI Intelligence**: [Google Gemini API](https://ai.google.dev/) via `google-genai` SDK with strict JSON output schemas.
- **Deterministic Routing & Fallback**: Internal rule engine (`routing.py`, `ev_config.py`) providing zero-latency, offline classification and SLA calculation whenever Gemini is unavailable or rate-limited.
- **Data & Analytics**: [Pandas](https://pandas.pydata.org/) and [Plotly Express](https://plotly.com/python/) for operational metrics, station outage trends, and SLA performance reporting.

---

## Application Workflows

### 1. Customer Workflow
- **Submit EV Charging Complaints**: Select from VoltWay's network stations (e.g., Baner Central Charging Hub, Hinjawadi Tech Park Hub), specify vehicle model (e.g., Tata Nexon EV), and optionally enter transaction and charging session IDs.
- **View Ticket History**: Dedicated **My ticket history** tab displays all submitted complaints, urgency levels, assigned departments, and current resolution status.
- **Track Responses**: View live status updates (`Open`, `In Progress`, `Awaiting Customer`, `Resolved`, `Closed`) and read official support responses once approved by an administrator.

### 2. Administrator Workflow
- **Operations Overview**: Real-time KPI metrics for active tickets, awaiting approval queue, escalated incidents, and SLA breaches.
- **Ticket Management**: Filter tickets by urgency and status; inspect EV complaint details (Station ID, Session ID, Transaction ID, Vehicle Model).
- **AI Intelligence Review**: Inspect AI-generated issue summary, sentiment, urgency classification, and escalation rationale.
- **Human-in-the-Loop Approval**: Edit suggested draft responses, adjust assigned departments, approve responses for customer viewing, and update ticket resolution status.
- **Analytics & SLA Monitoring**: Visual charts for complaint patterns by station, city, department workload, and resolution SLA compliance rates.

---

## EV Department Routing & SLA Matrix

| Category | Primary Team | Default SLA | Escalation Trigger | Escalated SLA |
| :--- | :--- | :--- | :--- | :--- |
| **Safety Incident** | Safety Operations | Immediate | Smoke, fire, electric shock, sparks | Immediate human response |
| **Account & Application** | Account Support | 4 hours | Fraudulent transaction, account takeover | Immediate human response |
| **Payment & Billing** | Payment Support | 2 hours | Payment deducted without charge, double charge | 2 hours (priority review) |
| **Charging Failure** | Technical Operations | 2 hours | Connector error, session failure | 2 hours (priority review) |
| **Station Availability** | Network Operations | 1 hour | Entire network outage, station offline | 30 minutes / Immediate |
| **Refund & Transaction** | Finance Support | 4 hours | Legal threat / chargeback dispute | 30 minutes (escalated) |
| **General Inquiry** | General Support | 8 hours | Standard inquiry | 8 hours |

---

## Setup & Running the Application

### 1. Environment Activation (Windows PowerShell)

```powershell
# Navigate to project directory
cd C:\PyCharm\Support_Ticket_AI

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update `.env` based on `.env.example`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_NAME=Support Administrator
ADMIN_EMAIL=admin@supportai.com
ADMIN_PASSWORD=your_secure_admin_password
```

> **Note**: Public customer registration is open on the login screen. The administrator account is automatically provisioned from `.env` credentials if not already existing.

### 3. Launch Streamlit Application

```powershell
python -m streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## Running the Verification Test Suite

The project includes automated regression tests covering the 6 core business scenarios, fallback logic, and customer/admin workflow integration:

```powershell
# Test the 6 core EV business scenarios (Fallback and Live modes)
python test_scenarios.py

# Test Customer and Administrator end-to-end workflow integration
python test_workflows.py

# Test fallback engine keyword classification
python test_fallback.py

# Test EV domain intelligence and routing assertions
python test_ev_intelligence.py

# Verify station configuration
python test_ev_config.py
```

---

## Data Notice & Operational Constraints

- **VoltWay Networks** is a fictional EV network operator created for simulation, demonstration, and evaluation purposes.
- All charging stations, session IDs, and customer records are sample data.
- Approving a suggested response updates the database record for customer visibility; it does not trigger external email transmissions or mock bank payment gateway calls.
- Human approval is mandatory before any AI-generated response is visible to the customer.
