# InboxOps

An AI-assisted email operations dashboard. This MVP runs with realistic demo data and is structured for Gmail OAuth and LLM integrations.

## Run locally

### Frontend

```powershell
npm install
npm run dev
```

Open http://localhost:5173.

### Backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

The frontend defaults to local demo data if the API is unavailable. With the API running it uses `http://localhost:8000/api`.

## MVP features

- Searchable, filterable priority inbox
- Explainable classification and priority scoring
- Thread summaries and structured action extraction
- Editable AI reply drafts with selectable tone
- Explicit approval required before sending
- Follow-up reminders
- Analytics focused on inbox workload
- Prompt-injection-safe processing boundary (email content is treated as untrusted data)

## Production integration path

1. Create a Google Cloud OAuth client and request minimal Gmail scopes.
2. Replace `DemoEmailRepository` with a Gmail-backed repository.
3. Encrypt refresh tokens using a managed secret/KMS key.
4. Replace the deterministic intelligence service with an LLM provider using structured outputs.
5. Add PostgreSQL and a scheduler for durable reminders.

## Automation

The API starts a durable background worker that periodically synchronizes
connected inboxes, updates local search and smart sections, checks follow-ups,
and creates persistent notifications for due work. Configure it in
`backend/.env`; inspect `/api/automation/status`, `/api/automation/runs`, and
`/api/notifications`. Gmail Pub/Sub watches are optional via
`GMAIL_PUBSUB_TOPIC`.

Email sends and Calendar writes deliberately remain approval-gated. Docker
Compose provides a single-instance deployment and GitHub Actions verifies the
frontend and backend. Public deployment additionally requires HTTPS,
application authentication, a managed database, and a managed encryption key.
