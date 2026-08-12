"""InboxOps API. Demo-safe today; Gmail/LLM adapters can replace these services."""
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from . import automation, calendar_ops, gmail, intelligence, operations, production, smart_sections, workspace

@asynccontextmanager
async def lifespan(app:FastAPI):
    automation.start();yield;automation.stop()
app = FastAPI(title="InboxOps API", version="0.2.0",lifespan=lifespan)
app.middleware("http")(production.auth_middleware)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])

class Reply(BaseModel):
    body: str
    account_id: str | None = None
    to: str | None = None
    subject: str | None = None
    thread_id: str | None = None
    message_id: str | None = None

class ReminderIn(BaseModel):
    email_id: str
    when: str

class ComposeIn(BaseModel):
    account_id: str
    to: str
    subject: str
    body: str
    cc: str | None = None
    bcc: str | None = None
    thread_id: str | None = None
    reply_to_id: str | None = None
    idempotency_key: str | None = None

class LabelsIn(BaseModel):
    add: list[str] = []
    remove: list[str] = []

class DurableReminderIn(BaseModel):
    title: str
    remind_at: str
    account_id: str | None = None
    thread_id: str | None = None
    condition_type: str = "time"

class IntelligenceIn(BaseModel):
    account_id: str = ""
    subject: str
    body: str
    sender: str = ""
    date: str = ""

class DraftIntelligenceIn(IntelligenceIn):
    tone: str = "Professional"
    instruction: str | None = None

class FollowupIn(BaseModel):
    account_id: str
    thread_id: str
    subject: str
    due_at: str

class PrivacyIn(BaseModel):
    hosted_ai_enabled: bool = True
    redact_pii: bool = True
    allow_accounts: list[str] = []
    retain_ai_results: bool = False
    attachment_ai_enabled: bool = False

class TaskIn(BaseModel):
    title: str
    notes: str | None = None
    status: str = "pending"
    priority: int = 50
    due_at: str | None = None
    account_id: str | None = None
    thread_id: str | None = None

class TaskPatch(BaseModel):
    title: str | None = None
    notes: str | None = None
    status: str | None = None
    priority: int | None = None
    due_at: str | None = None

class ContactPatch(BaseModel):
    vip: bool | None = None
    notes: str | None = None
    importance: int | None = None

class ProfileIn(BaseModel):
    signature: str | None = None
    tone: str | None = None
    preferences: dict | None = None

class FreeBusyIn(BaseModel):
    account_id: str
    time_min: str
    time_max: str
    time_zone: str = "Asia/Kolkata"

class CalendarEventIn(BaseModel):
    account_id: str
    summary: str
    start: str
    end: str
    description: str = ""
    location: str | None = None
    time_zone: str = "Asia/Kolkata"
    attendees: list[str] = []
    notify_attendees: bool = False

reminders = [{"id":"r1","emailId":"e5","title":"Follow up with Noah","when":"Tomorrow, 10:00 AM","status":"scheduled"}]
oauth_states: dict[str,str] = {}

@app.get("/api/health")
def health(): return {"status":"ok","service":"inboxops"}

@app.get("/api/readiness")
def readiness():return production.readiness()

@app.get("/api/automation/status")
def automation_status():return automation.status()

@app.post("/api/automation/run")
def automation_run():automation.cycle();return automation.status()

@app.get("/api/automation/runs")
def automation_runs():return automation.runs()

@app.get("/api/notifications")
def get_notifications(unread_only:bool=False):return automation.notifications(unread_only)

@app.post("/api/notifications/{notification_id}/read")
def read_notification(notification_id:str):return {"updated":automation.mark_read(notification_id)}

@app.post("/api/gmail/watch/{account_id}")
def gmail_watch(account_id:str):
    try:return automation.enable_gmail_watch(account_id)
    except Exception as exc:raise HTTPException(502,f"Gmail watch failed: {exc}") from exc

@app.get("/api/auth/google/start")
def google_start():
    try: url,state=gmail.authorization_url()
    except Exception as exc: raise HTTPException(500,str(exc)) from exc
    oauth_states[state]="gmail"
    return {"authorizationUrl":url}

@app.get("/api/auth/google/calendar/start")
def google_calendar_start():
    try: url,state=gmail.authorization_url(gmail.SCOPES+gmail.CALENDAR_SCOPES)
    except Exception as exc: raise HTTPException(500,str(exc)) from exc
    oauth_states[state]="calendar"
    return {"authorizationUrl":url}

@app.get("/api/auth/google/callback")
def google_callback(request: Request, state: str, code: str | None = None, error: str | None = None):
    if error: return RedirectResponse(f"http://127.0.0.1:5173/?gmail=error&reason={error}")
    if state not in oauth_states or not code: raise HTTPException(400,"Invalid or expired OAuth state")
    purpose=oauth_states.pop(state)
    try:
        scopes=gmail.SCOPES+gmail.CALENDAR_SCOPES if purpose=="calendar" else gmail.SCOPES
        flow=gmail.oauth_flow(state,scopes); flow.fetch_token(authorization_response=str(request.url)); gmail.save_credentials(flow.credentials)
    except Exception as exc: raise HTTPException(400,f"Google connection failed: {exc}") from exc
    return RedirectResponse(f"http://127.0.0.1:5173/?{purpose}=connected")

@app.get("/api/accounts")
def get_accounts(): return gmail.accounts()

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: str): return {"disconnected":gmail.disconnect(account_id)}

@app.get("/api/emails")
def get_emails(account_id: str | None = None, limit: int = 20):
    connected=gmail.accounts()
    if not connected: return []
    selected=[a for a in connected if not account_id or a["id"]==account_id]
    try:
        messages=[]
        for account in selected: messages.extend(gmail.list_messages(account["id"],limit))
        return messages
    except Exception as exc: raise HTTPException(502,f"Gmail sync failed: {exc}") from exc

@app.get("/api/gmail/threads")
def gmail_threads(account_id: str, page_token: str | None = None, limit: int = 20, q: str | None = None):
    try:
        if account_id=="all":
            items=[]
            for account in gmail.accounts(): items.extend(operations.list_threads(account["id"],None,limit,q)["items"])
            items.sort(key=lambda x:x.get("date",''),reverse=True)
            return {"items":items[:limit*max(1,len(gmail.accounts()))],"nextPageToken":None}
        return operations.list_threads(account_id,page_token,limit,q)
    except Exception as exc: raise HTTPException(502,f"Thread sync failed: {exc}") from exc

@app.get("/api/gmail/threads/{thread_id}")
def gmail_thread(thread_id: str, account_id: str):
    try: return operations.get_thread(account_id,thread_id)
    except Exception as exc: raise HTTPException(502,f"Thread fetch failed: {exc}") from exc

@app.patch("/api/gmail/threads/{thread_id}/labels")
def gmail_modify_labels(thread_id: str, account_id: str, data: LabelsIn):
    try: return operations.modify_thread(account_id,thread_id,data.add,data.remove)
    except Exception as exc: raise HTTPException(502,f"Gmail action failed: {exc}") from exc

@app.get("/api/gmail/labels")
def gmail_labels(account_id: str):
    try: return operations.labels(account_id)
    except Exception as exc: raise HTTPException(502,f"Label fetch failed: {exc}") from exc

@app.get("/api/smart-sections")
def get_smart_sections(account_id: str, selected: str = ""):
    try: return smart_sections.overview(account_id, selected.split(",") if selected else None)
    except Exception as exc: raise HTTPException(502,f"Smart sections failed: {exc}") from exc

@app.get("/api/smart-sections/catalog")
def get_smart_section_catalog():
    return [{"id":key,"name":value["name"]} for key,value in smart_sections.SECTIONS.items()]

@app.post("/api/smart-sections/sync")
def sync_smart_sections(account_id: str, limit: int = 50, selected: str = ""):
    try: return smart_sections.sync(account_id, limit, selected.split(",") if selected else None)
    except Exception as exc: raise HTTPException(502,f"Smart section sync failed: {exc}") from exc

@app.get("/api/gmail/messages/{message_id}/attachments/{attachment_id}")
def gmail_attachment(message_id: str, attachment_id: str, account_id: str, filename: str="attachment"):
    try: content=operations.attachment(account_id,message_id,attachment_id)
    except Exception as exc: raise HTTPException(502,f"Attachment download failed: {exc}") from exc
    safe_name=filename.replace('"','')
    return Response(content,media_type="application/octet-stream",headers={"Content-Disposition":f'attachment; filename="{safe_name}"'})

@app.get("/api/gmail/messages/{message_id}/attachments/{attachment_id}/text")
def gmail_attachment_text(message_id: str,attachment_id: str,account_id: str,mime_type: str="application/octet-stream",filename: str="attachment"):
    try:return operations.attachment_text(account_id,message_id,attachment_id,mime_type,filename)
    except Exception as exc:raise HTTPException(502,f"Attachment extraction failed: {exc}") from exc

@app.post("/api/gmail/drafts")
def gmail_draft(data: ComposeIn):
    try: return operations.create_draft(data.account_id,data.to,data.subject,data.body,data.cc,data.bcc,data.thread_id,data.reply_to_id)
    except Exception as exc: raise HTTPException(502,f"Draft creation failed: {exc}") from exc

@app.post("/api/gmail/send")
def gmail_send(data: ComposeIn):
    if not data.idempotency_key: raise HTTPException(400,"idempotency_key is required")
    try: return operations.send(data.account_id,data.to,data.subject,data.body,data.idempotency_key,data.cc,data.bcc,data.thread_id,data.reply_to_id)
    except Exception as exc: raise HTTPException(502,f"Gmail send failed: {exc}") from exc

@app.get("/api/operations/reminders")
def durable_reminders(): return operations.reminders()

@app.get("/api/operations/reminders/due")
def reminders_due(): return operations.due_reminders()

@app.post("/api/operations/reminders")
def create_durable_reminder(data: DurableReminderIn):
    return operations.save_reminder(str(uuid4()),data.title,data.remind_at,data.account_id,data.thread_id,data.condition_type)

@app.post("/api/operations/reminders/{reminder_id}/complete")
def finish_reminder(reminder_id: str): return {"completed":operations.complete_reminder(reminder_id)}

@app.post("/api/intelligence/analyze")
def analyze_email(data: IntelligenceIn):
    subject,body,privacy=workspace.prepare_ai(data.account_id,data.subject,data.body,"analyze")
    result=intelligence.smart_analyze(subject,body,data.sender,data.date) if privacy["hostedAllowed"] else intelligence.analyze(subject,body,data.sender,data.date)
    workspace.audit(data.account_id,"analyze",result.get("provider","local"),privacy["redacted"]);result["privacy"]=privacy;return result

@app.post("/api/intelligence/draft")
def intelligent_draft(data: DraftIntelligenceIn):
    subject,body,privacy=workspace.prepare_ai(data.account_id,data.subject,data.body,"draft")
    profile=workspace.profile(data.account_id) if data.account_id else {"tone":data.tone,"signature":""}
    tone=data.tone or profile.get("tone","Professional")
    personalization=f"{data.instruction or ''}\nUse this signature exactly: {profile.get('signature','')}".strip()
    result=intelligence.smart_draft(subject,body,data.sender,tone,personalization) if privacy["hostedAllowed"] else intelligence.draft_reply(subject,body,data.sender,tone,personalization)
    if not result.get("provider") and profile.get("signature"):
        result["draft"]=result["draft"].rsplit("\n\n",1)[0]+"\n\n"+profile["signature"]
    workspace.audit(data.account_id,"draft",result.get("provider","local"),privacy["redacted"]);result["privacy"]=privacy;return result

@app.get("/api/intelligence/daily-brief")
def inbox_daily_brief(account_id: str):
    try: page=operations.list_threads(account_id,limit=25); return intelligence.daily_brief(page["items"])
    except Exception as exc: raise HTTPException(502,f"Daily brief failed: {exc}") from exc

@app.get("/api/operations/followups")
def get_followups(): return operations.list_followups()

@app.post("/api/operations/followups")
def add_followup(data: FollowupIn):
    try:return operations.create_followup(str(uuid4()),data.account_id,data.thread_id,data.subject,data.due_at)
    except Exception as exc:raise HTTPException(502,f"Follow-up creation failed: {exc}") from exc

@app.get("/api/operations/followups/check")
def check_followups():
    try:return operations.check_followups()
    except Exception as exc:raise HTTPException(502,f"Follow-up check failed: {exc}") from exc

@app.get("/api/privacy")
def get_privacy(): return workspace.privacy()

@app.put("/api/privacy")
def put_privacy(data: PrivacyIn): return workspace.save_privacy(data.model_dump())

@app.get("/api/privacy/audit")
def privacy_audit(): return workspace.audits()

@app.post("/api/search/index")
def build_search_index(account_id: str):
    selected=gmail.accounts() if account_id=="all" else [a for a in gmail.accounts() if a["id"]==account_id];count=0
    try:
        for account in selected:
            page=operations.list_threads(account["id"],limit=50)
            for item in page["items"]:
                thread=operations.get_thread(account["id"],item["threadId"]);latest=thread["messages"][-1]
                workspace.upsert_document({"id":latest["id"],"account_id":account["id"],"thread_id":latest["threadId"],"subject":latest["subject"],"sender":latest["from"],"body":latest["bodyText"],"received_at":latest["date"]});count+=1
                workspace.record_contact(latest["from"],latest["from"],latest["date"])
        return {"indexed":count,"localOnly":True}
    except Exception as exc: raise HTTPException(502,f"Indexing failed: {exc}") from exc

@app.get("/api/search")
def semantic_search(q: str, account_id: str | None=None): return workspace.search(q,None if account_id=="all" else account_id)

@app.get("/api/tasks")
def get_tasks(): return workspace.tasks()

@app.post("/api/tasks")
def add_task(data: TaskIn): return workspace.create_task(data.model_dump())

@app.patch("/api/tasks/{task_id}")
def patch_task(task_id: str,data: TaskPatch): return workspace.update_task(task_id,data.model_dump(exclude_none=True))

@app.get("/api/contacts")
def get_contacts(): return workspace.contacts()

@app.patch("/api/contacts/{email}")
def patch_contact(email: str,data: ContactPatch): return workspace.update_contact(email,data.model_dump(exclude_none=True))

@app.get("/api/writing-profile/{account_id}")
def get_writing_profile(account_id: str): return workspace.profile(account_id)

@app.put("/api/writing-profile/{account_id}")
def put_writing_profile(account_id: str,data: ProfileIn): return workspace.save_profile(account_id,data.model_dump(exclude_none=True))

@app.get("/api/calendar/status/{account_id}")
def calendar_status(account_id: str): return calendar_ops.status(account_id)

@app.post("/api/calendar/freebusy")
def calendar_freebusy(data: FreeBusyIn):
    try: return calendar_ops.freebusy(data.account_id,data.time_min,data.time_max,data.time_zone)
    except PermissionError as exc: raise HTTPException(409,str(exc)) from exc
    except Exception as exc: raise HTTPException(502,f"Calendar availability failed: {exc}") from exc

@app.post("/api/calendar/events")
def calendar_create(data: CalendarEventIn):
    try: return calendar_ops.create_event(data.account_id,data.model_dump(exclude={"account_id"}))
    except PermissionError as exc: raise HTTPException(409,str(exc)) from exc
    except Exception as exc: raise HTTPException(502,f"Calendar event creation failed: {exc}") from exc

@app.get("/api/reminders")
def get_reminders(): return reminders

@app.post("/api/reminders")
def create_reminder(data: ReminderIn):
    item={"id":str(uuid4()),"emailId":data.email_id,"title":"Follow up reminder","when":data.when,"status":"scheduled"}
    reminders.append(item)
    return item

@app.post("/api/emails/{email_id}/draft")
def draft(email_id: str, tone: str = "Professional"):
    concise = tone.lower() == "concise"
    body = "Hi,\n\nThanks for reaching out. This works well for me.\n\nBest,\nAditya" if concise else "Hi,\n\nThank you for reaching out. This sounds good — I'll review the details and get back to you shortly.\n\nBest,\nAditya"
    return {"emailId":email_id,"tone":tone,"draft":body}

@app.post("/api/emails/{email_id}/send")
def approve_send(email_id: str, reply: Reply):
    if not all([reply.account_id,reply.to,reply.subject]):
        return {"status":"demo","emailId":email_id,"message":"Demo message was not externally sent"}
    try: result=gmail.send_reply(reply.account_id,reply.to,reply.subject,reply.body,reply.thread_id,reply.message_id)
    except Exception as exc: raise HTTPException(502,f"Gmail send failed: {exc}") from exc
    return {"status":"sent","emailId":result.get("id"),"threadId":result.get("threadId"),"approvedAt":datetime.utcnow().isoformat()}
