SupportAI – corrected local version
This pack updates three connected parts of the current project.
Files to replace
- app.py – corrected customer/admin dashboards and unique Streamlit widget keys.
- database.py – SQLite users and tickets, including migration of missing ticket columns.
- llm_service.py – Gemini plus local Python fallback.
- requirements.txt – dependencies.
Files to add
- test_fallback.py – tests internal fallback without making Gemini calls.
- README_UPGRADE.md – these instructions.
Keep your existing routing.py, .env, .streamlit/config.toml, and support_tickets.db.
Important: back up your database
Before replacing database.py, copy support_tickets.db to a safe location. The updated database module adds missing columns to the existing tickets table and does not delete existing ticket rows.
Configure .env
GEMINI_API_KEY=your_new_gemini_key
ADMIN_NAME=Support Administrator
ADMIN_EMAIL=admin@supportai.com
ADMIN_PASSWORD=choose_a_strong_password
Admin account creation occurs once if the configured email does not already exist. Public registration only creates customer accounts. Do not share .env or commit it to GitHub. If a key was previously exposed, revoke it and create a replacement.
Install and run (PyCharm PowerShell terminal)
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
Test local fallback (does not call Gemini)
python test_fallback.py
Important behavior
- Every admin ticket widget key includes both ticket ID and the display section (admin_overview or admin_queue), fixing the duplicate key error.
- The same uniqueness is applied to text areas, select boxes, and action buttons.
- If Gemini key is missing, SDK cannot load, model is unavailable, quota is exceeded, service is busy, or a request fails, the Python fallback returns a classification and a draft response.
- The fallback is rule-based and less nuanced than Gemini; the ticket clearly records Rule-Based Fallback.
- Existing tickets without a customer ID remain visible to admins but are not attached to a customer account.
- Admin approval records approval in the database; it does not send an email.
This is a local development build, not yet a deployed production system.