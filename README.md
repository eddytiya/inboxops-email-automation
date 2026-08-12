# InboxOps - AI Email Operations Automation

InboxOps is a local-first email automation platform designed to reduce repetitive inbox work while keeping consequential actions under human control.

It connects to Gmail, synchronizes conversations, classifies emails into smart sections, extracts priorities and action items, generates reply drafts, tracks follow-ups, schedules reminders, creates persistent notifications, and integrates with Google Calendar.

The system automates inbox monitoring and decision support, but it does not send emails or create calendar events without explicit user approval.

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

<img width="542" height="370" alt="image" src="https://github.com/user-attachments/assets/f9363afc-b44d-47aa-a5cd-f8863b4a8924" />


### 7. Automation status and run history

Show the automation status or run-history response, including successful inbox synchronization and follow-up checks. This can be captured from the application or `/api/automation/status` and `/api/automation/runs`.

<img width="817" height="867" alt="image" src="https://github.com/user-attachments/assets/d14885ff-b076-415f-946b-fccf384699ec" />
<img width="797" height="808" alt="image" src="https://github.com/user-attachments/assets/7f2a2f87-ce9b-49b9-ac5b-ea4e2574de61" />



### 8. Calendar workflow

Show availability checking or the calendar event review screen before the user approves event creation.

<img width="1127" height="850" alt="image" src="https://github.com/user-attachments/assets/66e89959-2cfd-4ead-b710-21086613e420" />




### 9. Search, tasks, and contacts

Show local inbox search results, extracted tasks, or contact prioritization.

<img width="1117" height="846" alt="image" src="https://github.com/user-attachments/assets/f3ed06ce-eee4-4724-8c1b-0f92f3085182" />


### 10. CI automation

Show the green GitHub Actions check demonstrating that frontend validation, production build, and backend tests pass automatically.

<img width="1437" height="592" alt="image" src="https://github.com/user-attachments/assets/ca46787d-775b-416b-be10-07aeaadc0784" />


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



---

## Project Overview

Managing email manually often involves repeatedly checking the inbox, identifying important messages, categorizing conversations, remembering follow-ups, extracting deadlines, writing similar replies, and monitoring whether someone has responded.

InboxOps combines these activities into one operational workspace.

The application provides:

- Live Gmail synchronization
- Automated email classification
- Priority scoring and explanations
- AI-generated summaries and action items
- Approval-gated reply drafting
- Reminder and follow-up monitoring
- Persistent notifications
- Local inbox search
- Task and contact intelligence
- Google Calendar integration
- Background automation with retries and run history

---

## Why This Project Is Local-First

InboxOps is intended primarily as a personal or internal workflow automation system. It runs locally so Gmail data, OAuth tokens, search indexes, reminders, contacts, and automation records remain under the user's control.

A local-first architecture provides several advantages:

- Personal email data is not exposed through a public deployment.
- OAuth credentials and tokens remain on the local machine.
- Search and attachment extraction can run locally.
- External AI access can be controlled or disabled.
- The application can be demonstrated without building a public multi-user SaaS platform.
- Every user can operate the automation with their own Google account and credentials.

The project can be deployed with Docker, but public multi-user deployment requires additional authentication, managed secrets, a production database, HTTPS, and user-level data isolation.

---

## Core Automation Workflow

```text
Gmail account
      ↓
Periodic inbox synchronization
      ↓
Thread and attachment processing
      ↓
Classification and priority analysis
      ↓
Search, tasks, contacts, and smart sections
      ↓
Reminder and follow-up monitoring
      ↓
Persistent notifications
      ↓
Human-approved email or calendar action
```

---

# Features

## Gmail Integration

- Google OAuth account connection
- Encrypted OAuth token storage
- Support for connected Gmail accounts
- Inbox and conversation synchronization
- Full Gmail thread retrieval
- Gmail search-query support
- Label retrieval and modification
- Read and unread state management
- Star and archive operations
- Gmail draft creation
- Thread-aware reply creation
- CC and BCC support
- Duplicate-send protection using idempotency keys
- Gmail account disconnection
- Optional Gmail Pub/Sub watch registration

---

## Automated Classification

InboxOps can classify conversations into configurable smart sections.

Examples include:

- Jobs and recruiters
- Payments and invoices
- Meetings
- Support requests
- Newsletters
- Follow-ups
- Sports
- Entertainment
- Urgent conversations
- Messages requiring a reply

Classification results can be reflected through Gmail labels and displayed inside the InboxOps sidebar.

---

## Priority Intelligence

InboxOps analyzes email content and generates operational intelligence such as:

- Priority score
- Priority explanation
- Email category
- Conversation summary
- Latest update
- Required action
- Extracted deadline
- Important people
- Important decisions
- Waiting-on status
- Suggested tasks
- Dates and times
- Monetary amounts
- Phone numbers
- Relevant links

The system can use Gemini or OpenAI when configured. If no hosted AI provider is available, it falls back to deterministic local analysis.

---

## AI Reply Drafting

InboxOps can generate contextual email drafts using:

- Professional tone
- Friendly tone
- Concise tone
- Formal tone
- Assertive tone
- Custom instructions
- Stored writing preferences
- User-defined signature

Generated drafts remain editable.

> **Important:** InboxOps never sends a generated reply automatically. The user must review and confirm the final message before it is sent.

---

## Daily Intelligence Brief

The Daily Brief reviews recent inbox conversations and produces:

- Total conversations reviewed
- Number of urgent conversations
- Number of likely replies
- Estimated focus time
- Ranked priorities
- Sender and subject context
- Explanation for each priority

The brief can be opened through the AI Brief navigation item or the bottom operations bar.

---

## Reminder Automation

Users can schedule reminders directly from an email conversation.

Each reminder can contain:

- Reminder title
- Scheduled time
- Gmail account reference
- Conversation reference
- Current status

A background worker checks for due reminders and converts them into persistent notifications.

---

## Follow-Up Monitoring

InboxOps can monitor whether a conversation receives a reply.

When follow-up monitoring is enabled, the system:

1. Records the current thread message count.
2. Stores the follow-up deadline.
3. Periodically checks the Gmail thread.
4. Detects whether a new message was received.
5. Marks the follow-up as replied when appropriate.
6. Creates an alert if the deadline passes without a response.
7. Prevents repeated duplicate alerts for the same follow-up.

---

## Persistent Notifications

Notifications are stored in the local database instead of existing only inside the browser.

The notification system supports:

- Reminder notifications
- Follow-up alerts
- Unread notification state
- Read timestamps
- Conversation references
- Account references
- Browser desktop notifications when permission is granted

Because notifications are persistent, due work can be discovered by the backend even when the frontend is not actively open.

---

## Attachment Processing

InboxOps supports attachment discovery and downloading through Gmail.

Local extraction is available for:

- Plain-text files
- PDF documents
- DOCX documents

Attachment processing includes extraction limits and privacy controls. Attachment content does not need to be sent to a hosted AI provider.

---

## Private Inbox Search

InboxOps creates a local searchable index of synchronized conversations using SQLite FTS5.

Search features include:

- Full-text subject search
- Sender search
- Email-body search
- Account-specific filtering
- Synonym expansion
- Local-only processing

Example synonym expansion includes:

```text
invoice → payment, receipt, bill
job → interview, recruiter, application
meeting → call, schedule, calendar
urgent → ASAP, deadline, today
```

---

## Email Task Management

Users can create and manage tasks connected to email operations.

Task properties include:

- Title
- Notes
- Status
- Priority
- Due date
- Gmail account
- Conversation reference
- Creation timestamp
- Completion timestamp

---

## Contact Intelligence

InboxOps records contact interaction information locally.

Contact intelligence includes:

- Contact name and email
- Message count
- Reply count
- Last interaction
- Importance score
- Manual VIP status
- Contact notes

Importance is calculated from interaction frequency while VIP status remains a manual user decision.

---

## Writing Profiles

Each connected account can maintain a local writing profile containing:

- Preferred tone
- Email signature
- Writing preferences
- Accepted-writing sample count

These preferences can be used when generating reply drafts.

---

## Google Calendar Integration

Calendar permissions are requested separately from Gmail permissions.

Supported Calendar operations include:

- Calendar connection-status checking
- Free/busy availability lookup
- Time-zone support
- Event preparation
- Event description and location
- Attendee management
- Optional attendee notifications
- Approval-gated event creation

InboxOps does not autonomously create calendar events.

---

# Background Automation Engine

The FastAPI backend starts a background automation worker when the service launches.

By default, the worker runs every five minutes.

Each automation cycle can:

1. Find connected Gmail accounts.
2. Synchronize recent conversations.
3. Update the local search index.
4. Update contact records.
5. Classify messages into smart sections.
6. Check due reminders.
7. Check monitored follow-ups.
8. Detect new replies.
9. Create persistent notifications.
10. Record job results and errors.

The interval is configurable through environment variables.

---

# Reliability Features

InboxOps includes several reliability controls:

- Automatic retry handling
- Exponential retry backoff
- Durable automation-run history
- Attempt counting
- Start and finish timestamps
- Success and failure status
- Recorded error messages
- Recorded job details
- Duplicate-send prevention
- Duplicate follow-up alert prevention
- Health and readiness endpoints
- Graceful background-worker shutdown

---

# Human Approval and Safety Boundaries

InboxOps distinguishes between low-risk automation and consequential external actions.

### Automatically Permitted Operations

- Reading authorized Gmail data
- Synchronizing conversations
- Classifying emails
- Calculating priorities
- Extracting tasks and deadlines
- Creating local search records
- Checking reminders
- Monitoring follow-ups
- Generating drafts
- Creating internal notifications

### Explicit Approval Required

- Sending an email
- Sending an AI-generated reply
- Creating a Google Calendar event
- Notifying calendar attendees

This approach keeps automation useful without allowing it to make irreversible communication decisions independently.

---

# Privacy and Security

InboxOps includes:

- Encrypted OAuth token storage
- Local encryption-key generation
- OAuth state validation
- Configurable Gmail scopes
- Separate Calendar permissions
- Prompt-injection-resistant AI boundaries
- PII redaction before hosted AI processing
- Per-account hosted-AI permissions
- Attachment-AI controls
- AI activity audit records
- Optional API bearer authentication
- Mandatory authentication checks in production mode
- Constant-time token comparison
- Production readiness checks
- Git exclusions for credentials and private data

Email content is treated as untrusted data. Instructions contained inside an email are never treated as application commands.

Sensitive local paths excluded from Git include:

```gitignore
backend/.env
backend/secrets/
backend/data/
.venv/
node_modules/
dist/
```

---

# Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Lucide React
- Responsive CSS
- Browser Notification API

## Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLite
- SQLite FTS5
- Google Gmail API
- Google Calendar API
- Google OAuth
- Cryptography/Fernet
- PDF and DOCX text extraction

## Optional AI Providers

- Google Gemini
- OpenAI Responses API
- Deterministic local fallback

## Development and Delivery

- Git
- GitHub
- GitHub Actions
- Docker
- Docker Compose
- Pytest
- TypeScript compiler
- Vite production build

---

# Project Structure

```text
inboxops-email-automation/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── automation.py
│   │   ├── calendar_ops.py
│   │   ├── gmail.py
│   │   ├── intelligence.py
│   │   ├── main.py
│   │   ├── operations.py
│   │   ├── production.py
│   │   ├── security.py
│   │   ├── smart_sections.py
│   │   └── workspace.py
│   ├── tests/
│   │   └── test_automation.py
│   ├── .env.example
│   └── requirements.txt
├── src/
│   ├── InboxApp.tsx
│   ├── OperationsDock.tsx
│   ├── ControlCenter.tsx
│   ├── ReminderNotifications.tsx
│   ├── gmailApi.ts
│   ├── api.ts
│   ├── types.ts
│   └── stylesheets
├── Dockerfile
├── docker-compose.yml
├── package.json
├── pnpm-lock.yaml
├── vite.config.ts
└── README.md
```

---

# Local Installation

## Prerequisites

Install:

- Node.js 20 or newer
- npm or pnpm
- Python 3.12
- Git
- A Google Cloud project
- Gmail API access
- Optional Google Calendar API access

---

## Frontend Setup

Open a terminal:

```powershell
cd "D:\Automation\Email"
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

---

## Backend Setup

Open a second terminal:

```powershell
cd "D:\Automation\Email"

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r backend\requirements.txt

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Backend documentation:

```text
http://127.0.0.1:8000/docs
```

Backend health check:

```text
http://127.0.0.1:8000/api/health
```

---

# Environment Configuration

Copy:

```text
backend/.env.example
```

to:

```text
backend/.env
```

Important settings include:

```env
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/auth/google/callback

AUTOMATION_ENABLED=true
AUTOMATION_INTERVAL_SECONDS=300
SYNC_MESSAGE_LIMIT=50
AUTO_CLASSIFY=true

OPENAI_API_KEY=
OPENAI_MODEL=

GEMINI_API_KEY=
GEMINI_MODEL=

GMAIL_PUBSUB_TOPIC=

INBOXOPS_ENV=development
INBOXOPS_REQUIRE_AUTH=false
SESSION_COOKIE_SECURE=false

DATABASE_URL=
TOKEN_ENCRYPTION_KEY=
```

> **Never commit the real `.env` file.**

---

# Google OAuth Configuration

To connect Gmail:

1. Create a Google Cloud project.
2. Enable the Gmail API.
3. Create an OAuth consent screen.
4. Create a Desktop or Web OAuth client.
5. Configure the callback URL:

```text
http://127.0.0.1:8000/api/auth/google/callback
```

6. Store the downloaded client JSON inside:

```text
backend/secrets/
```

7. Add the Gmail account as an OAuth test user if the application remains in testing mode.
8. Start the backend and frontend.
9. Use the InboxOps Gmail connection flow.

For Calendar features, enable the Google Calendar API and grant the additional Calendar scopes.

---

# Important API Endpoints

## System

```http
GET /api/health
GET /api/readiness
```

## Gmail

```http
GET    /api/accounts
GET    /api/gmail/threads
GET    /api/gmail/threads/{thread_id}
PATCH  /api/gmail/threads/{thread_id}/labels
POST   /api/gmail/drafts
POST   /api/gmail/send
```

## Intelligence

```http
POST /api/intelligence/analyze
POST /api/intelligence/draft
GET  /api/intelligence/daily-brief
```

## Automation

```http
GET  /api/automation/status
GET  /api/automation/runs
POST /api/automation/run
```

## Reminders and Follow-Ups

```http
GET  /api/operations/reminders
POST /api/operations/reminders
GET  /api/operations/reminders/due
POST /api/operations/reminders/{reminder_id}/complete

GET  /api/operations/followups
POST /api/operations/followups
GET  /api/operations/followups/check
```

## Notifications

```http
GET  /api/notifications
POST /api/notifications/{notification_id}/read
```

## Search and Workspace

```http
POST /api/search/index
GET  /api/search
GET  /api/tasks
POST /api/tasks
GET  /api/contacts
GET  /api/privacy
PUT  /api/privacy
```

## Calendar

```http
GET  /api/calendar/status/{account_id}
POST /api/calendar/freebusy
POST /api/calendar/events
```

---

# Verification

## Frontend Type-Check

```powershell
npm run typecheck
```

## Frontend Production Build

```powershell
npm run build
```

## Backend Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q backend\tests
```

## Backend Compilation

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend
```

---

# Continuous Integration

GitHub Actions automatically runs on pushes and pull requests.

The CI workflow verifies:

- Dependency installation
- TypeScript validation
- Frontend production build
- Python dependency installation
- Backend automation tests

This provides automated evidence that both the frontend and backend remain operational after code changes.

---

# Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

Docker provides:

- Multi-stage frontend and backend build
- Persistent application data
- Persistent secrets directory
- Container health checks
- Automatic service restart

For this portfolio project, local execution is recommended because it avoids exposing personal Gmail data through a public deployment.

---

# Current Limitations

InboxOps is a portfolio-ready local automation system, not a finished public SaaS product.

Current limitations include:

- SQLite is used instead of PostgreSQL.
- The scheduler runs inside the API process.
- Public multi-user account isolation is not implemented.
- Gmail Pub/Sub requires separate Google Cloud configuration.
- Hosted AI requires a configured provider key.
- Browser desktop notifications require browser permission.
- Google OAuth may require approved test users.
- Public deployment requires HTTPS and managed secrets.
- Calendar event creation currently relies on API-level approval flows.
- Email and Calendar writes remain intentionally approval-gated.

---

# Recommended Demonstration Flow

For a portfolio demonstration:

1. Start the backend and frontend.
2. Connect a dedicated demonstration Gmail account.
3. Synchronize the inbox.
4. Run smart-section classification.
5. Open a classified email.
6. Generate AI insights.
7. Show its priority score and explanation.
8. Generate a reply draft.
9. Demonstrate the approval-before-send boundary.
10. Schedule a reminder.
11. Enable no-reply follow-up monitoring.
12. Trigger an automation cycle.
13. Show automation run history.
14. Show persistent notifications.
15. Demonstrate local search, tasks, and contact intelligence.
16. Show the successful GitHub Actions workflow.

> **Tip:** Use a dedicated demo account and avoid displaying personal messages or credentials.

---

# Portfolio Value

This project demonstrates practical experience with:

- Workflow automation
- Background scheduling
- Gmail and Calendar APIs
- OAuth authentication
- AI-assisted information extraction
- Human-in-the-loop automation
- Secure token handling
- Prompt-injection boundaries
- Persistent reminders and notifications
- Retry and idempotency design
- Local full-text search
- React interface development
- FastAPI backend development
- Automated CI testing
- Docker-based packaging

---

# Safety Statement

InboxOps is designed as a decision-support and workflow-automation system.

It can automatically discover, synchronize, classify, summarize, prioritize, monitor, and notify.

It **cannot autonomously send emails or create calendar events without user approval**.

This boundary is intentional.

---

# Repository

Source code:

[github.com/eddytiya/inboxops-email-automation](https://github.com/eddytiya/inboxops-email-automation)

---

# Author

**Edditya**

Automation and AI workflow portfolio project.
