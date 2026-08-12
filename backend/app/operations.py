"""Complete Gmail operations and durable reminder storage."""
from __future__ import annotations
import base64, hashlib, html, io, re, sqlite3, zipfile
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any
from .gmail import db, service
from pypdf import PdfReader

def init_tables() -> None:
    con=db()
    con.execute("""CREATE TABLE IF NOT EXISTS send_log(idempotency_key TEXT PRIMARY KEY, account_id TEXT NOT NULL, gmail_message_id TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    con.execute("""CREATE TABLE IF NOT EXISTS reminders(id TEXT PRIMARY KEY, account_id TEXT, thread_id TEXT, title TEXT NOT NULL, remind_at TEXT NOT NULL, condition_type TEXT DEFAULT 'time', status TEXT DEFAULT 'scheduled', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    con.execute("""CREATE TABLE IF NOT EXISTS followups(id TEXT PRIMARY KEY, account_id TEXT NOT NULL, thread_id TEXT NOT NULL, subject TEXT, due_at TEXT NOT NULL, baseline_count INTEGER NOT NULL, status TEXT DEFAULT 'waiting', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    con.commit()

def _headers(payload: dict) -> dict[str,str]:
    return {h["name"].lower():h["value"] for h in payload.get("headers",[])}

def _decode(data: str|None) -> bytes:
    return base64.urlsafe_b64decode((data or "")+"===")

def _parts(payload: dict) -> tuple[str,str,list[dict]]:
    plain=""; rich=""; attachments=[]
    def walk(part: dict):
        nonlocal plain,rich
        mime=part.get("mimeType",""); body=part.get("body",{}); filename=part.get("filename","")
        if filename and body.get("attachmentId"):
            attachments.append({"id":body["attachmentId"],"filename":filename,"mimeType":mime,"size":body.get("size",0)})
        elif body.get("data"):
            decoded=_decode(body["data"]).decode("utf-8","replace")
            if mime=="text/plain" and not plain: plain=decoded
            elif mime=="text/html" and not rich: rich=decoded
        for child in part.get("parts",[]): walk(child)
    walk(payload)
    if not plain and rich: plain=re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",rich))).strip()
    return plain,rich,attachments

def normalize_message(account_id: str, msg: dict) -> dict[str,Any]:
    h=_headers(msg["payload"]); plain,rich,attachments=_parts(msg["payload"]); sender=h.get("from","Unknown")
    return {"id":msg["id"],"accountId":account_id,"threadId":msg["threadId"],"messageId":h.get("message-id"),"from":sender,"to":h.get("to",""),"cc":h.get("cc",""),"subject":h.get("subject","(No subject)"),"date":h.get("date",""),"snippet":msg.get("snippet",""),"bodyText":plain,"bodyHtml":rich,"attachments":attachments,"labels":msg.get("labelIds",[]),"unread":"UNREAD" in msg.get("labelIds",[]),"starred":"STARRED" in msg.get("labelIds",[])}

def list_threads(account_id: str, page_token: str|None=None, limit: int=20, query: str|None=None) -> dict:
    api=service(account_id); kwargs={"userId":"me","labelIds":["INBOX"],"maxResults":min(limit,50)}
    if page_token: kwargs["pageToken"]=page_token
    if query: kwargs["q"]=query
    result=api.users().threads().list(**kwargs).execute(); threads=[]
    for item in result.get("threads",[]):
        raw=api.users().threads().get(userId="me",id=item["id"],format="metadata",metadataHeaders=["From","To","Subject","Date","Message-ID"]).execute(); msgs=raw.get("messages",[]); latest=normalize_message(account_id,msgs[-1]); latest["messageCount"]=len(msgs); threads.append(latest)
    return {"items":threads,"nextPageToken":result.get("nextPageToken")}

def get_thread(account_id: str, thread_id: str) -> dict:
    raw=service(account_id).users().threads().get(userId="me",id=thread_id,format="full").execute()
    return {"id":thread_id,"accountId":account_id,"messages":[normalize_message(account_id,m) for m in raw.get("messages",[])]}

def modify_thread(account_id: str, thread_id: str, add: list[str]|None=None, remove: list[str]|None=None):
    return service(account_id).users().threads().modify(userId="me",id=thread_id,body={"addLabelIds":add or [],"removeLabelIds":remove or []}).execute()

def labels(account_id: str) -> list[dict]:
    return service(account_id).users().labels().list(userId="me").execute().get("labels",[])

def attachment(account_id: str, message_id: str, attachment_id: str) -> bytes:
    data=service(account_id).users().messages().attachments().get(userId="me",messageId=message_id,id=attachment_id).execute()["data"]
    return _decode(data)

def attachment_text(account_id:str,message_id:str,attachment_id:str,mime_type:str,filename:str)->dict:
    content=attachment(account_id,message_id,attachment_id);text="";kind="unsupported"
    if mime_type.startswith("text/"):
        text=content.decode("utf-8","replace");kind="text"
    elif mime_type=="application/pdf" or filename.lower().endswith(".pdf"):
        reader=PdfReader(io.BytesIO(content));text="\n".join(page.extract_text() or "" for page in reader.pages[:30]);kind="pdf"
    elif filename.lower().endswith(".docx"):
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            xml=archive.read("word/document.xml").decode("utf-8","replace");text=re.sub(r"<[^>]+>"," ",xml);text=html.unescape(re.sub(r"\s+"," ",text));kind="docx"
    return {"filename":filename,"kind":kind,"text":text[:100000],"characters":len(text),"localOnly":True}

def _mime(to: str, subject: str, body: str, cc: str|None=None, bcc: str|None=None, reply_to_id: str|None=None) -> str:
    msg=EmailMessage(); msg["To"]=to; msg["Subject"]=subject; msg.set_content(body)
    if cc: msg["Cc"]=cc
    if bcc: msg["Bcc"]=bcc
    if reply_to_id: msg["In-Reply-To"]=reply_to_id; msg["References"]=reply_to_id
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()

def create_draft(account_id: str, to: str, subject: str, body: str, cc: str|None=None, bcc: str|None=None, thread_id: str|None=None, reply_to_id: str|None=None):
    payload={"message":{"raw":_mime(to,subject,body,cc,bcc,reply_to_id)}}
    if thread_id: payload["message"]["threadId"]=thread_id
    return service(account_id).users().drafts().create(userId="me",body=payload).execute()

def send(account_id: str, to: str, subject: str, body: str, idempotency_key: str, cc: str|None=None, bcc: str|None=None, thread_id: str|None=None, reply_to_id: str|None=None):
    init_tables(); con=db(); existing=con.execute("SELECT gmail_message_id FROM send_log WHERE idempotency_key=?",(idempotency_key,)).fetchone()
    if existing: return {"id":existing["gmail_message_id"],"duplicatePrevented":True}
    payload={"raw":_mime(to,subject,body,cc,bcc,reply_to_id)}
    if thread_id: payload["threadId"]=thread_id
    result=service(account_id).users().messages().send(userId="me",body=payload).execute()
    con.execute("INSERT INTO send_log(idempotency_key,account_id,gmail_message_id) VALUES(?,?,?)",(idempotency_key,account_id,result["id"])); con.commit()
    result["duplicatePrevented"]=False; return result

def save_reminder(reminder_id: str, title: str, remind_at: str, account_id: str|None=None, thread_id: str|None=None, condition_type: str="time") -> dict:
    init_tables(); con=db(); con.execute("INSERT INTO reminders(id,account_id,thread_id,title,remind_at,condition_type) VALUES(?,?,?,?,?,?)",(reminder_id,account_id,thread_id,title,remind_at,condition_type)); con.commit(); return get_reminder(reminder_id)

def get_reminder(reminder_id: str) -> dict:
    row=db().execute("SELECT * FROM reminders WHERE id=?",(reminder_id,)).fetchone(); return dict(row) if row else {}

def reminders() -> list[dict]:
    init_tables(); return [dict(r) for r in db().execute("SELECT * FROM reminders ORDER BY remind_at")]

def due_reminders() -> list[dict]:
    init_tables(); now=datetime.now(timezone.utc).isoformat(); return [dict(r) for r in db().execute("SELECT * FROM reminders WHERE status='scheduled' AND remind_at<=? ORDER BY remind_at",(now,))]

def complete_reminder(reminder_id: str) -> bool:
    con=db(); cur=con.execute("UPDATE reminders SET status='done' WHERE id=?",(reminder_id,)); con.commit(); return cur.rowcount>0

def create_followup(followup_id:str,account_id:str,thread_id:str,subject:str,due_at:str) -> dict:
    init_tables(); raw=service(account_id).users().threads().get(userId="me",id=thread_id,format="minimal").execute(); count=len(raw.get("messages",[]));con=db();con.execute("INSERT INTO followups(id,account_id,thread_id,subject,due_at,baseline_count) VALUES(?,?,?,?,?,?)",(followup_id,account_id,thread_id,subject,due_at,count));con.commit();return dict(con.execute("SELECT * FROM followups WHERE id=?",(followup_id,)).fetchone())

def check_followups() -> list[dict]:
    init_tables();con=db();rows=con.execute("SELECT * FROM followups WHERE status='waiting'").fetchall();alerts=[];now=datetime.now(timezone.utc).isoformat()
    for row in rows:
        raw=service(row["account_id"]).users().threads().get(userId="me",id=row["thread_id"],format="minimal").execute();count=len(raw.get("messages",[]))
        if count>row["baseline_count"]: con.execute("UPDATE followups SET status='replied' WHERE id=?",(row["id"],))
        elif row["due_at"]<=now:
            alerts.append(dict(row));con.execute("UPDATE followups SET status='alerted' WHERE id=?",(row["id"],))
    con.commit();return alerts

def list_followups() -> list[dict]:
    init_tables();return [dict(r) for r in db().execute("SELECT * FROM followups ORDER BY due_at")]
