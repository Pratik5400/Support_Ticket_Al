# ⚡ SupportAI · VoltWay Networks
### Enterprise AI-Powered EV Charging Support & NOC Incident Triage Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-MongoDB%207.0+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Google%20Gemini%202.5-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Security](https://img.shields.io/badge/Security-PBKDF2--SHA256%20(310k)-blueviolet?style=for-the-badge)](https://en.wikipedia.org/wiki/PBKDF2)
[![Test Suite](https://img.shields.io/badge/Automated%20Tests-100%25%20Passing-00C853?style=for-the-badge)](https://github.com/)

**An intelligent customer care and Network Operations Center (NOC) ticketing system custom-engineered for Electric Vehicle (EV) public charging networks.**

[⚡ Quick Start](#quick-start) •
[📖 Project Overview](#project-overview) •
[🎯 Problem & Solution](#problem-statement) •
[✨ Key Features](#key-features) •
[🏗️ Architecture](#system-architecture) •
[🚦 Routing & SLAs](#routing-and-slas) •
[📊 NOC Operations](#visual-walkthrough) •
[🧪 Verification](#testing-and-verification)

</div>

---

<a id="quick-start"></a>
## ⚡ Quick Start

Get SupportAI running on your local machine in under **2 minutes**:

```powershell
# 1. Clone & enter repository
git clone https://github.com/your-username/Support_Ticket_AI.git
cd Support_Ticket_AI

# 2. Create and activate a Python 3.12 virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1       # On Windows PowerShell (or: source .venv/bin/activate on Linux/macOS)

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Launch the application
python -m streamlit run app.py
```

> [!TIP]
> **Zero Configuration Required**: The platform starts out-of-the-box! If no `GEMINI_API_KEY` is provided in `.env`, the system transparently utilizes its built-in **Deterministic EV Rule Fallback Engine** with zero downtime.

Open **`http://localhost:8501`** in your browser.

- **Default Administrator Credentials**: Configured automatically via `.env` (defaults: `admin@example.com` / `admin12345`).
- **Customer Access**: Click the **Create customer account** tab on the login screen to register a new EV driver profile.

---

<a id="project-overview"></a>
## 📖 Project Overview

Public EV charging networks operate in high-stress, real-world conditions where physical hardware, high-voltage power electronics, cellular communications, and banking rails converge. When an EV driver experiences a failure at a charging kiosk (such as a locked cable connector, mid-session charging drop, or payment deduction without electricity delivery), generic customer support queues create multi-day delays that leave motorists stranded.

**SupportAI** is a domain-tailored operational platform built for **VoltWay Networks**—a public charging network managing AC and DC fast-charging hubs across **Pune, Mumbai, and Nashik**. 

By orchestrating **Google Gemini 2.5 Flash** with a **sub-millisecond deterministic fallback engine**, SupportAI instantly parses unstructured customer complaints, identifies urgent physical safety hazards, routes tickets to specialized engineering teams, calculates SLA deadlines, and drafts empathetic responses protected by a strict **Human-in-the-Loop** operational safeguard.

```
       ┌─────────────────┐
       │   EV Customer   │ ── Submits issue: "Charged ₹500 via UPI, but charger failed"
       └────────┬────────┘
                │
                ▼
  ╔═══════════════════════════╗
  ║    SupportAI Engine       ║ ── Triage in < 15ms (Gemini AI / Offline Rule Fallback)
  ╚═══════════════════════════╝
    ├── 🏷️ Category:           Payment & Billing
    ├── ⚡ Urgency:            High
    ├── 🛠️ Assigned Team:      Payment Support
    ├── ⏱️ SLA Target:         2 hours (Priority Review)
    └── 📝 Suggested Reply:    "We verified your payment and session logs..."
                │
                ▼
       ┌─────────────────┐
       │  NOC Operator   │ ── Inspects, edits, & approves reply (Human-in-the-Loop)
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │   EV Customer   │ ── Sees verified official response in Driver Portal
       └─────────────────┘
```

---

<a id="problem-statement"></a>
## 🎯 Problem Statement & EV Domain Friction

Public EV charging operations face distinct failure modes that generic helpdesks are unequipped to handle:

| Operational Failure Mode | Real-World Impact | How SupportAI Solves It |
| :--- | :--- | :--- |
| **Payment / Session Mismatch** | UPI/card debited, but connector handshake fails; driver is out of pocket without charge. | Auto-triaged to **Payment Support** under *Priority Review* with transaction tracking and 2-hour SLA. |
| **Connector Jam / Cable Lock** | CCS2 or Type 2 connector remains mechanically locked in vehicle socket. | Flagged as **Charging Failure**, dispatched to **Technical Operations** for remote unlock or dispatch. |
| **Thermal / Safety Hazard** | Cable overheating, burning smell, sparks, or exposed electrical wiring. | Bypasses standard queues; triggers **Critical** alert, instructs driver to move away, alerts **Safety Operations**. |
| **Mid-Session Power Drop** | 120kW DC fast charger abruptly terminates after 3 minutes due to thermal throttling. | Classified as **Charging Failure**, tagged with EV model and charging speed for technical diagnostics. |
| **Station Network Outage** | Station communication drops offline due to cellular modem or cloud gateway fault. | Routed to **Network Operations** with a 1-hour urgent SLA to minimize network-wide downtime. |
| **Account Takeover / Fraud** | Driver suspects compromised credentials or unauthorized charging billing. | Instantly classified under **Account & Application** with immediate human intervention SLA. |

---

<a id="key-features"></a>
## ✨ Key Features

### 🚗 EV Driver Customer Portal
- **Intuitive Complaint Submission**: Free-text complaint input with live charging station selector.
- **Interactive Station Telemetry**: Visual card displaying station area, city, charger type (`DC Fast Charger` vs `AC Charger`), power rating (`60 kW` / `120 kW` / `22 kW`), and live operational status (`Operational` vs `Maintenance`).
- **Session & Vehicle Metadata**: Captures optional Transaction ID, Session ID, and EV vehicle model (e.g., *Tata Nexon EV*, *MG ZS EV*, *Mahindra XUV400*).
- **Driver Ticket Stream ("My Ticket History")**: Real-time ticket history with color-coded status badges, urgency indicators, SLA targets, and **official approved NOC responses**.

### 🛡️ Administrator NOC Command Center
- **Live KPI Status Strip**: Real-time counter metrics for **Total Tickets**, **Awaiting Approval**, **Escalated Incidents**, **Active Tickets**, and **Resolved Tickets**.
- **Three-Tier Operational View**:
  1. **⚡ Live Overview**: Rapid triage cards for incoming complaints requiring immediate attention.
  2. **📋 Ticket Queue & Triage**: Complete filterable queue by Urgency (`Critical`, `High`, `Medium`, `Low`) and Status (`Open`, `In Progress`, `Awaiting Customer`, `Resolved`, `Closed`).
  3. **📊 Network Analytics & SLA**: Plotly-powered executive charts tracking monthly ticket trends, category breakdowns, station complaint rankings, city-level distributions, and SLA compliance gauges.
- **Human-in-the-Loop Response Workflow**: Operators inspect AI-suggested responses, refine phrasing via an inline editor, reassign teams or update ticket statuses, and release official replies with single-click approval.
- **Operational Data Export**: One-click download of all ticket data formatted as an operations CSV report (`voltway_operations_report.csv`).

### 🧠 Dual-Mode Intelligence & Resilience
- **Google Gemini 2.5 Flash API**: Context-aware NLP analyzing customer sentiment, extracting root issues, assessing urgency, and drafting professional customer service replies.
- **10-Second API Timeout Guard**: Client requests enforce a strict 10-second timeout to prevent UI thread hangs during high network latency.
- **Zero-Downtime Deterministic Fallback**: Automatic keyword triage engine matching comprehensive domain failure terms. Guarantees 100% platform uptime even if the Gemini API is offline, unconfigured, or rate-limited.

### 🔒 Enterprise Security & Scalability
- **Cryptographic Password Security**: PBKDF2-HMAC-SHA256 password hashing with **310,000 rounds** and unique 16-byte random salts.
- **MongoDB NoSQL Persistence**: Scalable runtime database (`voltway_supportai`) with atomic auto-increment counters and compound indexing for rapid search.
- **Strict Data Integrity**: Preserves historical legacy tickets in a local SQLite archive (`support_tickets.db`).

---

<a id="system-architecture"></a>
## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Clients["Client Presentation Layer"]
        Driver["🚗 EV Driver (Customer Portal)"]
        Admin["🛡️ NOC Engineer (Admin Control Panel)"]
    end

    subgraph AppLayer["Streamlit Application Engine (app.py)"]
        RouterUI["Streamlit UI & Routing Controllers"]
        AuthSystem["PBKDF2 Authentication & Session Manager"]
    end

    subgraph TriageEngine["Intelligence & Triage Pipeline"]
        LLM["Google Gemini API (llm_service.py)"]
        Fallback["Zero-Latency Rule-Based Fallback"]
        BusinessRouter["Deterministic EV Routing Engine (routing.py)"]
        DomainConfig["VoltWay Domain Config & Keywords (ev_config.py)"]
    end

    subgraph Persistence["Persistence & Database Layer"]
        MongoDB[("MongoDB 7.0+ (voltway_supportai)\nusers | tickets | counters")]
        LegacyDB[("SQLite Benchmark Archive\nsupport_tickets.db")]
    end

    %% Interactions
    Driver -->|"Submit Complaint + Metadata"| RouterUI
    Admin -->|"Inspect, Edit, Reassign & Approve"| RouterUI
    RouterUI <--> AuthSystem
    AuthSystem <-->|"Verify Salted Hash"| MongoDB

    RouterUI -->|"Raw Complaint Text"| LLM
    LLM -.->|"On Timeout / Disconnect / Quota"| Fallback
    DomainConfig -->|"Supply Keywords"| Fallback
    LLM -->|"Category, Urgency, Draft"| BusinessRouter
    Fallback -->|"Category, Urgency, Draft"| BusinessRouter
    DomainConfig -->|"SLA & Team Rules"| BusinessRouter

    BusinessRouter -->|"Routed Ticket Document"| MongoDB
    MongoDB -->|"Display Queue & Plotly Analytics"| RouterUI
    MongoDB -.->|"Historical Benchmarks"| LegacyDB

    classDef clientStyle fill:#17283B,stroke:#48D9ED,stroke-width:2px,color:#F5F8FC;
    classDef appStyle fill:#1E334A,stroke:#48D9ED,stroke-width:2px,color:#F5F8FC;
    classDef aiStyle fill:#1A365D,stroke:#42D99B,stroke-width:2px,color:#F5F8FC;
    classDef dbStyle fill:#0D2A4A,stroke:#FFB84D,stroke-width:2px,color:#F5F8FC;

    class Driver,Admin clientStyle;
    class RouterUI,AuthSystem appStyle;
    class LLM,Fallback,BusinessRouter,DomainConfig aiStyle;
    class MongoDB,LegacyDB dbStyle;
```

### Architectural Layer Responsibilities

1. **Presentation Layer (`app.py`)**: Renders custom dark-navy (`#101C2C`) and electric-cyan (`#48D9ED`) user interfaces. Employs unique Streamlit widget namespaces (`admin_overview_...` vs `admin_queue_...`) to eliminate duplicate key collisions.
2. **Intelligence Layer (`llm_service.py` & `ev_config.py`)**: Manages the LLM inference lifecycle. Formats structured JSON prompts, validates schema compliance, and triggers internal fallback mechanisms upon network interruption.
3. **Routing Layer (`routing.py`)**: Implements strict hierarchical business rules:
   - **Safety First**: Smoke, fire, or sparks trigger instant escalation to **Safety Operations**.
   - **Security Second**: Account compromise triggers instant escalation to **Account Support**.
   - **Payment Reconciliation**: Payment deductions without charging map to **Payment Support** with priority review.
4. **Persistence Layer (`database.py`)**: Connects to MongoDB via `pymongo`, maintaining compound indexes for `(user_id, id DESC)` and `(ticket_status, sla_due_at ASC)`.

---

<a id="ticket-lifecycle"></a>
## 🔄 Ticket Processing Lifecycle

The diagram below illustrates the end-to-end lifecycle of a support ticket from driver submission to NOC resolution:

```mermaid
sequenceDiagram
    autonumber
    actor Driver as EV Customer
    participant App as Streamlit App (app.py)
    participant AI as AI Engine (llm_service.py)
    participant Router as Routing Engine (routing.py)
    participant DB as MongoDB (voltway_supportai)
    actor Admin as NOC Administrator

    Driver->>App: Submits complaint (Station, Session ID, Description)
    App->>AI: analyze_ticket(complaint_text)
    alt Gemini API Active
        AI->>AI: Gemini extracts Category, Urgency, Sentiment & Draft
    else Gemini Offline / Timeout (>10s)
        AI->>AI: Fallback keyword matching generates structured triage
    end
    AI-->>App: Raw triage dictionary
    App->>Router: route_ticket(triage_data, complaint_text)
    Router->>Router: Applies Safety/Security rules & calculates SLA deadline
    Router-->>App: Enriched ticket document
    App->>DB: save_ticket(...) [status: Open, approval: Pending]
    DB-->>Driver: Instant Ticket Confirmation (#ID)

    Admin->>App: Opens NOC Administrator Dashboard
    App->>DB: get_all_tickets()
    DB-->>Admin: Displays ticket in Triage Queue with AI draft
    Admin->>App: Reviews/edits suggested draft & clicks "Approve Response"
    App->>DB: update_approval_status(ticket_id, "Approved")
    
    Driver->>App: Views "My Ticket History"
    App->>DB: get_user_tickets(user_id)
    DB-->>Driver: Displays "Official VoltWay Support Response"
    
    Admin->>App: Marks ticket status as "Resolved"
    App->>DB: update_ticket_status(ticket_id, "Resolved") -> sets resolved_at
```

---

<a id="routing-and-slas"></a>
## 🚦 EV Domain Intelligence & Routing Engine

VoltWay Networks classifies customer issues into **7 specialized EV categories** and routes them deterministically to dedicated operational support departments.

### Support Departments & SLA Target Matrix

| Category | Assigned Team | Default Urgency | SLA Target | Escalation Condition |
| :--- | :--- | :---: | :---: | :--- |
| **Safety Incident** | **Safety Operations** | `Critical` | **Immediate human response** | Smoke, fire, sparks, burning odor, or electrical shock. |
| **Account & Application** | **Account Support** | `Critical` / `Medium` | **Immediate / 4 hours** | Unauthorized access, account takeover, or app login lockouts. |
| **Station Availability** | **Network Operations** | `Critical` / `High` | **1 hour** | Multiple stations offline, grid failure, or network-wide downtime. |
| **Payment & Billing** | **Payment Support** | `High` | **2 hours** | Amount debited but charging session failed to start; double charges. |
| **Charging Failure** | **Technical Operations** | `High` | **2 hours** | Connector locked in vehicle socket, PLC handshake error, mid-session stop. |
| **Refund & Transaction** | **Finance Support** | `Medium` | **4 hours** | Transaction reconciliation, wallet balance inquiries, refund status. |
| **General Inquiry** | **General Support** | `Low` / `Medium` | **8 hours** | Tariffs, operational hub hours, membership tiers, EV compatibility. |

### The 6 Core Benchmark Business Scenarios

SupportAI is verified against 6 mission-critical business scenarios:

```
[Scenario 1: Payment/Charging Mismatch]
Complaint: "Paid ₹500 at Baner Hub via UPI, amount deducted but charger failed to start."
├── Category:   Payment & Billing
├── Urgency:    High
├── Team:       Payment Support
├── Escalation: Priority Review
└── SLA Target: 2 hours (priority review)

[Scenario 2: Charger Connector Jam]
Complaint: "Tata Nexon EV at Baner Hub. Charger displays connector error and won't initiate."
├── Category:   Charging Failure
├── Urgency:    High
├── Team:       Technical Operations
├── Escalation: Priority Review
└── SLA Target: 2 hours (priority review)

[Scenario 3: Mid-Session Power Interruption]
Complaint: "DC fast charging session at Hinjawadi stopped abruptly after 5 minutes."
├── Category:   Charging Failure
├── Urgency:    High
├── Team:       Technical Operations
├── Escalation: Priority Review
└── SLA Target: 2 hours (priority review)

[Scenario 4: Duplicate Billing]
Complaint: "Charged twice for a single charging session. Two deductions of ₹650 on my card."
├── Category:   Payment & Billing
├── Urgency:    High
├── Team:       Payment Support
├── Escalation: Priority Review
└── SLA Target: 2 hours (priority review)

[Scenario 5: Account Takeover & Fraud]
Complaint: "Fraudulent transaction on my account. Someone accessed my account without authorization."
├── Category:   Account & Application
├── Urgency:    Critical
├── Team:       Account Support
├── Escalation: Escalated
└── SLA Target: Immediate human response

[Scenario 6: Tariff & Hours Inquiry]
Complaint: "What is the tariff per kWh at Mumbai DC hubs and what are your support hours?"
├── Category:   General Inquiry
├── Urgency:    Medium / Low
├── Team:       General Support
├── Escalation: Normal
└── SLA Target: 8 hours
```

---

<a id="visual-walkthrough"></a>
## 📊 Visual UI & Operational Walkthrough

### 1. EV Driver Experience

```
+---------------------------------------------------------------------------------------+
|  ⚡ VoltWay Networks · Driver Support Portal                         [Logged in: Rahul] |
+---------------------------------------------------------------------------------------+
|  [ ⚡ Report an EV Charging Issue ]    [ 📋 My Ticket History (2) ]                     |
|                                                                                       |
|  Select Charging Station: [ VLT-PUN-001 | Baner Central Charging Hub (Pune) ▼ ]       |
|  +---------------------------------------------------------------------------------+  |
|  | 📍 Area: Baner, Pune  |  ⚡ Type: DC Fast Charger  |  ⚡ Power: 60 kW  |  ● Operational  |  |
|  +---------------------------------------------------------------------------------+  |
|                                                                                       |
|  Vehicle Model: [ Tata Nexon EV               ]  Transaction ID: [ TXN-94810294     ] |
|  Session ID:    [ SES-440182                  ]  Subject:        [ Amount deducted   ] |
|                                                                                       |
|  Describe the problem in detail:                                                      |
|  +---------------------------------------------------------------------------------+  |
|  | ₹500 was deducted from my UPI account, but the charger never started charging.   |  |
|  | The screen showed 'Handshake Timeout'. Please assist immediately.               |  |
|  +---------------------------------------------------------------------------------+  |
|                                                                                       |
|  [ 🚀 Submit Support Ticket ]                                                         |
+---------------------------------------------------------------------------------------+
```

### 2. Administrator NOC Command Center

```
+---------------------------------------------------------------------------------------+
|  🛡️ VoltWay Networks · Network Operations Center (NOC)               [Role: Admin]    |
+---------------------------------------------------------------------------------------+
|  [ Total: 42 ]   [ Awaiting Approval: 7 ]   [ Escalated: 3 ]   [ Active: 12 ]   [ Resolved: 27 ]|
+---------------------------------------------------------------------------------------+
|  [ ⚡ Live Overview ]    [ 📋 Ticket Queue & Triage ]    [ 📊 Network Analytics & SLA ] |
|                                                                                       |
|  TICKET #104  |  High Urgency  |  Payment Support  |  Due in: 1h 45m  |  Status: Open |
|  Customer: Rahul Sharma (rahul@example.com)  |  Station: Baner Central Charging Hub   |
|  Complaint: "₹500 was deducted from my UPI account, but the charger never started..."|
|                                                                                       |
|  Suggested Response (Gemini 2.5 AI Draft - Pending Approval):                         |
|  +---------------------------------------------------------------------------------+  |
|  | Dear Rahul, thank you for reaching out. We have logged your report regarding     |  |
|  | session SES-440182 at Baner Central Hub. Our Payment Support team is verifying |  |
|  | the UPI transaction reference with our banking gateway...                       |  |
|  +---------------------------------------------------------------------------------+  |
|                                                                                       |
|  Reassign Team: [ Payment Support ▼ ]   Update Status: [ In Progress ▼ ]              |
|  [ ✅ Approve Response ]   [ 💾 Save Draft Edits ]   [ 🔄 Update Status ]             |
+---------------------------------------------------------------------------------------+
```

> [!NOTE]
> **Adding High-Resolution Screenshots**: To feature live screenshots in this repository, create the directory `assets/screenshots/` and add PNG image captures for:
> - `01_login_screen.png`: Split-screen authentication view.
> - `02_customer_submit.png`: Driver complaint form with station card preview.
> - `03_customer_history.png`: Driver ticket stream with live status badges.
> - `04_admin_overview.png`: NOC KPI metric cards and incoming triage cards.
> - `05_admin_approval.png`: Human-in-the-loop response editor and approval controls.
> - `06_admin_analytics.png`: Plotly charts showing SLA metrics and station rankings.

---

<a id="database-design"></a>
## 🗄️ Database Architecture & Schemas

SupportAI uses **MongoDB** as its primary active document store (`voltway_supportai`) and maintains an archived **SQLite** benchmark database (`support_tickets.db`).

### MongoDB Collections Design

#### 1. `users` Collection
Stores credential hashes and role authorization flags.

```json
{
  "_id": "ObjectId('6b0177c534a9a1d34ea19255')",
  "id": 1,
  "name": "Support Administrator",
  "email": "admin@example.com",
  "password_hash": "a4f8...$310000$digest...",
  "role": "admin",
  "created_at": "2026-11-21T16:21:49"
}
```
*Indexes*:
- `{"id": 1}` *(Unique)*
- `{"email": 1}` *(Unique)*

#### 2. `tickets` Collection
Stores full customer complaint payloads, technical metadata, AI diagnostics, and SLA timestamps.

<details>
<summary><b>Click to inspect sample Ticket Document</b></summary>

```json
{
  "_id": "ObjectId('6b0178b80eea9ce4e3c19996')",
  "id": 104,
  "user_id": 2,
  "subject": "Amount deducted but charging not started",
  "ticket_text": "₹500 was deducted from my UPI account, but the charging session never started...",
  "station_id": "VLT-PUN-001",
  "station_name": "Baner Central Charging Hub",
  "station_city": "Pune",
  "transaction_id": "TXN-94810294",
  "session_id": "SES-440182",
  "vehicle_model": "Tata Nexon EV",
  "category": "Payment & Billing",
  "urgency": "High",
  "sentiment": "Negative",
  "summary": "Driver was charged ₹500 via UPI; power delivery failed to initiate.",
  "draft_reply": "Dear Customer, we have initiated verification of your session...",
  "approval_status": "Pending",
  "assigned_team": "Payment Support",
  "escalation_status": "Priority Review",
  "rule_triggered": "EV Rule 5: Payment/Charging Mismatch",
  "sla_target": "2 hours (priority review)",
  "sla_due_at": "2026-11-23T13:25:52",
  "ticket_status": "Open",
  "analysis_mode": "Gemini AI",
  "model_used": "gemini-2.5-flash",
  "created_at": "2026-11-23T11:25:52",
  "updated_at": "2026-11-23T11:25:52",
  "resolved_at": null
}
```
</details>

*Indexes*:
- `{"id": 1}` *(Unique)*
- `{"user_id": 1, "id": -1}` *(Compound: Fast customer history retrieval)*
- `{"ticket_status": 1, "sla_due_at": 1}` *(Compound: Fast SLA monitoring and overdue triage)*

#### 3. `counters` Collection
Guarantees clean, auto-incrementing sequential integers for ticket references (`#1`, `#2`, `#3`...) using MongoDB's atomic `find_one_and_update` with `$inc`.

---

<a id="ai-engine"></a>
## 🤖 AI Engine & Resilience Fallback

```
[Incoming Complaint] ──► [Try Google Gemini API (10s Timeout)]
                                 │
             ┌───────────────────┴───────────────────┐
             ▼                                       ▼
      [Success: 200 OK]                   [Timeout / Network Error / 429]
      - Model: gemini-2.5-flash           - Triggers _fallback_analysis()
      - Strict JSON schema validation     - Keyword parsing from ev_config.py
      - Tagged: "Gemini AI"               - Tagged: "Rule-Based Fallback"
             │                                       │
             └───────────────────┬───────────────────┘
                                 ▼
                 [routing.py Deterministic Rules]
                 - Enforces Safety / Security overrides
                 - Sets exact SLA deadlines & department
```

### 1. Google Gemini API Pipeline
When an API key is configured, `llm_service.py` queries candidate models (`gemini-2.5-flash-lite`, `gemini-2.5-flash`, `gemini-2.0-flash`) via the modern `google-genai` SDK.
- **Strict Response Schema**: The model is prompted to output pure JSON matching required fields: `category`, `urgency`, `sentiment`, `summary`, `draft_reply`, `escalate`, and `escalation_reason`.
- **Anti-Hallucination Guardrail**: The system prompt strictly prohibits the AI from promising unverified refunds or claiming that field maintenance has been completed.

### 2. Deterministic EV Fallback Classifier
If external connectivity drops or API quotas are exhausted, `_fallback_analysis()` evaluates the complaint against authoritative domain keywords:

<details>
<summary><b>Click to inspect Fallback Keyword Dictionaries</b></summary>

- **Safety**: `smoke`, `fire`, `burning smell`, `overheating`, `electric shock`, `sparks`, `exposed wire`, `explosion`.
- **Security**: `account takeover`, `hacked`, `unauthorized access`, `compromised`, `fraudulent transaction`.
- **Outage**: `entire network is down`, `all stations are offline`, `critical network outage`, `network-wide outage`.
- **Payment & Billing**: `payment deducted`, `amount deducted`, `charged but`, `paid but`, `charged twice`, `double charge`.
- **Charging Failure**: `connector error`, `charging did not start`, `charging stopped`, `cable stuck`, `session failed`.
- **Station Availability**: `station offline`, `charger unavailable`, `station is down`.
- **Account & App**: `login`, `password`, `app crash`, `cannot access account`.
</details>

---

<a id="security-and-guardrails"></a>
## 🛡️ Security, Privacy & Guardrails

1. **Cryptographic Authentication**:
   - Passwords are never stored in plaintext. The system generates unique 16-byte cryptographic random salts and hashes passwords using `hashlib.pbkdf2_hmac("sha256", ...)` with **310,000 iterations**.
   - Verification uses constant-time `hmac.compare_digest` to prevent timing attacks.
2. **Human-in-the-Loop Response Delivery**:
   - AI drafts are stored in the database with `approval_status = "Pending"`.
   - Customers **only** see responses once a verified NOC Administrator inspects and explicitly clicks **Approve Response**.
3. **Environment Security**:
   - Database URIs and API credentials are read from `.env` and excluded from source control via `.gitignore`.
4. **Widget Key Isolation**:
   - Streamlit widget keys are namespaced dynamically with ticket IDs and tab identifiers to guarantee state isolation and prevent UI crashes.

---

<a id="folder-structure"></a>
## 📂 Project Directory Structure

```
Support_Ticket_AI/
├── .streamlit/
│   └── config.toml               # Streamlit theme settings (Navy #101C2C & Cyan #48D9ED)
├── data/
│   └── sample_stations.csv       # Charging hub catalog for Pune, Mumbai, Nashik
├── app.py                        # Main Streamlit application (Customer & NOC Admin views)
├── database.py                   # MongoDB persistence engine, indexing & PBKDF2 auth
├── ev_config.py                  # VoltWay business config, station directory & keyword maps
├── llm_service.py                # Gemini 2.5 SDK integration & deterministic fallback engine
├── routing.py                    # Deterministic EV routing rules, team assignment & SLAs
├── sample_tickets.csv            # Benchmark training and demonstration tickets
├── support_tickets.db            # Persistent legacy SQLite archive (15 records)
├── test_ai.py                    # Single-ticket Gemini AI / fallback integration test
├── test_ev_config.py             # Station catalog and configuration integrity test
├── test_ev_intelligence.py       # EV domain routing rules and classification test
├── test_fallback.py              # Local fallback classifier regression test
├── test_scenarios.py             # Full assertion suite for the 6 core business scenarios
├── requirements.txt              # Production Python package dependencies
├── .env.example                  # Environment configuration template
└── README.md                     # Comprehensive project documentation
```

---

<a id="installation-and-setup"></a>
## ⚙️ Detailed Installation & Setup

### Prerequisites
- **Python 3.10 to 3.12** installed on your workstation.
- **MongoDB Server** (Community Edition running locally on port `27017` or a MongoDB Atlas cloud URI).

### Step 1: Set Up Virtual Environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to create your local `.env`:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` with your preferred settings:

```env
# MongoDB Connection (Defaults to local MongoDB)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=voltway_supportai

# Google Gemini API Key (Optional: Leave empty for offline fallback)
GEMINI_API_KEY=your_gemini_api_key_here

# Administrator Credentials (Auto-provisioned on startup)
ADMIN_NAME=Support Administrator
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin12345
```

### Step 4: Verify MongoDB Connection
Ensure MongoDB is running locally or your Atlas connection is reachable:
```bash
python -c "import database; print('MongoDB Connected successfully!')"
```

### Step 5: Start SupportAI
```bash
python -m streamlit run app.py
```

---

<a id="testing-and-verification"></a>
## 🧪 Testing and Verification

SupportAI includes an automated test harness validating both rule-based fallback and live AI modes:

| Test Script | Target Functionality | Command | Status |
| :--- | :--- | :--- | :---: |
| **`test_scenarios.py`** | 6 Core Business Scenarios (Fallback & AI modes) | `python test_scenarios.py` | **`PASS (6/6)`** |
| **`test_fallback.py`** | Fallback Keyword Classifier Accuracy | `python test_fallback.py` | **`PASS (5/5)`** |
| **`test_ev_intelligence.py`** | Domain Routing Rules & SLA Assertions | `python test_ev_intelligence.py` | **`PASS (7/7)`** |
| **`test_ev_config.py`** | Station Directory & Schema Integrity | `python test_ev_config.py` | **`PASS`** |
| **`test_ai.py`** | Gemini API & Timeout Fallback Handling | `python test_ai.py` | **`PASS`** |

### Run the Test Suite

Execute all core test suites directly in your activated virtual environment:

```powershell
python test_scenarios.py
python test_fallback.py
python test_ev_intelligence.py
```

<details>
<summary><b>Click to inspect sample test output</b></summary>

```
=================================================================
RUNNING 6 CORE SCENARIOS IN [RULE-BASED FALLBACK] MODE
=================================================================
  [PASS] Scenario 1: Payment deducted but charging did not start
         Category: Payment & Billing | Urgency: High | Team: Payment Support | SLA: 2 hours
  [PASS] Scenario 2: EV charger connector error
         Category: Charging Failure | Urgency: High | Team: Technical Operations | SLA: 2 hours
  [PASS] Scenario 3: Charging session failure
         Category: Charging Failure | Urgency: High | Team: Technical Operations | SLA: 2 hours
  [PASS] Scenario 4: Duplicate payment
         Category: Payment & Billing | Urgency: High | Team: Payment Support | SLA: 2 hours
  [PASS] Scenario 5: Fraudulent transaction or unauthorized account access
         Category: Account & Application | Urgency: Critical | Team: Account Support | SLA: Immediate
  [PASS] Scenario 6: General customer inquiry
         Category: General Inquiry | Urgency: Medium | Team: General Support | SLA: 8 hours

=================================================================
FINAL RESULT: Fallback=True, Live/Resilient=True
=================================================================
All VoltWay fallback and routing tests passed.
```
</details>

---

<a id="troubleshooting"></a>
## 🔧 Troubleshooting & FAQ

<details>
<summary><b>1. "Could not connect to MongoDB" error on startup</b></summary>

**Cause**: The MongoDB service is not currently running on `localhost:27017`.  
**Solution**:
- On Windows: Open Services (`services.msc`), find **MongoDB Server**, and click **Start**. Alternatively, run `net start MongoDB` in an Administrator terminal.
- If using MongoDB Atlas: Update `MONGO_URI` in `.env` with your Atlas connection string (e.g., `mongodb+srv://user:pass@cluster.mongodb.net/`).
</details>

<details>
<summary><b>2. "ModuleNotFoundError: No module named 'dotenv'"</b></summary>

**Cause**: The script was run using the global system Python rather than the virtual environment Python.  
**Solution**: Activate the virtual environment (`.\.venv\Scripts\Activate.ps1`) or invoke Python directly via `.\.venv\Scripts\python.exe app.py`.
</details>

<details>
<summary><b>3. Why does the ticket show "Rule-Based Fallback" instead of "Gemini AI"?</b></summary>

**Cause**: No valid `GEMINI_API_KEY` was found in `.env`, the API request exceeded the 10-second timeout, or network access was restricted.  
**Solution**: The application is designed to function seamlessly in fallback mode. To enable live Gemini AI triage, obtain an API key from [Google AI Studio](https://aistudio.google.com/) and paste it into `.env`.
</details>

<details>
<summary><b>4. How do I reset the Administrator password?</b></summary>

**Solution**: Update `ADMIN_PASSWORD` in `.env` and restart the application. If the administrator user already exists in MongoDB, update the password directly via MongoDB Compass or delete the admin document in the `users` collection to allow automatic reprovisioning.
</details>

---

<a id="roadmap"></a>
## 🚀 Roadmap & Future Scope

- [ ] **OCPP 1.6J / 2.0.1 Direct Protocol Telemetry**: Ingest real-time Open Charge Point Protocol WebSocket telemetry to automatically correlate driver complaints with charger error codes (`GroundFailure`, `OverCurrentFailure`, `ConnectorLockFailure`).
- [ ] **Automated SMS & Email Dispatch**: Integrate SendGrid or Twilio webhooks to notify drivers immediately when an NOC operator approves their ticket response.
- [ ] **Payment Gateway Webhook Reconciliation**: Direct reconciliation with Razorpay/Stripe APIs to cross-verify transaction IDs and automate refund authorizations.
- [ ] **Driver CSAT Scoring**: Prompt drivers for a 1-to-5 star rating and feedback upon ticket resolution to track team performance.
- [ ] **Containerized Cloud Deployment**: Pre-built Docker and Helm charts for deployment to Google Cloud Run, AWS ECS, or Kubernetes.

---

## 📜 Project Metadata

- **Project**: SupportAI – VoltWay Networks
- **Domain**: Electric Vehicle Public Charging Infrastructure Operations
- **Target Role**: Customer Care, Field Engineering & NOC Incident Triage
- **Evaluation**: Built for Academic Evaluation and Technical Portfolio Demonstration

<div align="center">
<sub>Crafted with ⚡ for reliable electric vehicle mobility.</sub>
</div>
