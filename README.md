# InboxOps

An AI-assisted email operations dashboard. This MVP runs with realistic demo data and is structured for Gmail OAuth and LLM integrations.

## Screenshots and automation walkthrough

> Replace each placeholder below with a Markdown image after adding your screenshots to a `docs/screenshots/` directory. Example: `![InboxOps priority inbox](docs/screenshots/priority-inbox.png)`.

### 1. Root page — priority inbox

Show the complete InboxOps landing page with the sidebar, priority inbox, filters, account selector, and visible email cards.

<img width="911" height="955" alt="image" src="https://github.com/user-attachments/assets/6e08b9fb-eee7-4449-b488-74666e246fd3" />


### 2. Gmail account connection

Show the connected Gmail account or account connection panel. Hide personal email addresses, OAuth codes, and private messages if you use a real account.

<img width="568" height="1026" alt="image" src="https://github.com/user-attachments/assets/8945668b-32f6-4f91-ada3-638ba2a15978" />


### 3. Automated classification and prioritization

Show messages organized into smart sections with their priority scores, categories, and explanations.

<img width="462" height="1032" alt="image" src="https://github.com/user-attachments/assets/978bb1e6-d390-4a49-8e5b-d5b7b8517936" />


### 4. AI email analysis

Show a selected conversation with its summary, detected action, deadline, people, and extracted tasks.

<img width="907" height="568" alt="image" src="https://github.com/user-attachments/assets/44498f3d-7d05-4ffd-a1ab-4f60858df79b" />
<img width="288" height="292" alt="image" src="https://github.com/user-attachments/assets/711da7c8-5912-4b41-8f79-4c8f254a2e0f" />


### 5. AI reply draft with approval gate

Show a generated reply draft, tone selector, editing controls, and the explicit approval step before sending.

<img width="853" height="503" alt="image" src="https://github.com/user-attachments/assets/93a2db94-da5a-45a5-9f03-ca206212c294" />


### 6. Reminder and follow-up automation

Show a scheduled reminder or tracked follow-up and the persistent notification produced by the background worker.

**[Place image here — Automated reminder, follow-up, or notification]**

### 7. Automation status and run history

Show the automation status or run-history response, including successful inbox synchronization and follow-up checks. This can be captured from the application or `/api/automation/status` and `/api/automation/runs`.

**[Place image here — Background automation status and successful run history]**

### 8. Calendar workflow

Show availability checking or the calendar event review screen before the user approves event creation.

**[Place image here — Calendar availability and approval-gated event creation]**

### 9. Search, tasks, and contacts

Show local inbox search results, extracted tasks, or contact prioritization.

**[Place image here — Search, task tracking, and contact intelligence]**

### 10. CI automation

Show the green GitHub Actions check demonstrating that frontend validation, production build, and backend tests pass automatically.

**[Place image here — Successful GitHub Actions CI run]**

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
