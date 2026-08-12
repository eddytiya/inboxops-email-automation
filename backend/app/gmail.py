"""Google OAuth, encrypted local token storage, and Gmail API helpers."""
from __future__ import annotations
import base64, json, os, secrets, sqlite3
from email.message import EmailMessage
from pathlib import Path
from typing import Any
from cryptography.fernet import Fernet
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
SECRET_DIR = ROOT / "secrets"
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "inboxops.db"
KEY_PATH = SECRET_DIR / ".token-key"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.modify"]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.events", "https://www.googleapis.com/auth/calendar.events.freebusy"]
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/api/auth/google/callback")
# OAuthlib blocks HTTP by default. Google permits loopback HTTP redirects for local
# development, so relax transport security only for these two loopback hosts.
if REDIRECT_URI.startswith(("http://127.0.0.1:", "http://localhost:")):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

def credential_file() -> Path:
    candidates = list(SECRET_DIR.glob("google-oauth-client.json")) or list(SECRET_DIR.glob("client_secret_*.json"))
    if not candidates: raise RuntimeError("Google OAuth client JSON is missing from backend/secrets")
    return candidates[0]

def _fernet() -> Fernet:
    SECRET_DIR.mkdir(parents=True, exist_ok=True)
    if not KEY_PATH.exists(): KEY_PATH.write_bytes(Fernet.generate_key())
    return Fernet(KEY_PATH.read_bytes())

def db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT, picture TEXT, token BLOB NOT NULL, scopes TEXT, connected_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    con.commit(); return con

def oauth_flow(state: str|None=None, scopes: list[str]|None=None) -> Flow:
    flow=Flow.from_client_secrets_file(str(credential_file()), scopes=scopes or SCOPES, state=state)
    flow.redirect_uri=REDIRECT_URI
    return flow

def authorization_url(scopes: list[str]|None=None) -> tuple[str,str]:
    flow=oauth_flow(scopes=scopes); url,state=flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent select_account")
    return url,state

def save_credentials(creds: Credentials) -> dict[str,Any]:
    oauth=build("oauth2","v2",credentials=creds,cache_discovery=False)
    info=oauth.userinfo().get().execute(); account_id=info["id"]
    token_data={"token":creds.token,"refresh_token":creds.refresh_token,"token_uri":creds.token_uri,"client_id":creds.client_id,"client_secret":creds.client_secret,"scopes":list(creds.scopes or SCOPES)}
    encrypted=_fernet().encrypt(json.dumps(token_data).encode())
    con=db(); existing=con.execute("SELECT token FROM accounts WHERE id=?",(account_id,)).fetchone()
    if existing and not token_data["refresh_token"]:
        old=json.loads(_fernet().decrypt(existing["token"]).decode()); token_data["refresh_token"]=old.get("refresh_token"); encrypted=_fernet().encrypt(json.dumps(token_data).encode())
    con.execute("INSERT INTO accounts(id,email,name,picture,token,scopes) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET email=excluded.email,name=excluded.name,picture=excluded.picture,token=excluded.token,scopes=excluded.scopes",(account_id,info["email"],info.get("name"),info.get("picture"),encrypted,json.dumps(token_data["scopes"])))
    con.commit(); return {"id":account_id,"email":info["email"],"name":info.get("name"),"picture":info.get("picture")}

def accounts() -> list[dict[str,Any]]:
    return [dict(r) for r in db().execute("SELECT id,email,name,picture,connected_at FROM accounts ORDER BY connected_at")]

def credentials(account_id: str) -> Credentials:
    row=db().execute("SELECT token FROM accounts WHERE id=?",(account_id,)).fetchone()
    if not row: raise KeyError("Connected account not found")
    return Credentials.from_authorized_user_info(json.loads(_fernet().decrypt(row["token"]).decode()))

def service(account_id: str): return build("gmail","v1",credentials=credentials(account_id),cache_discovery=False)

def disconnect(account_id: str) -> bool:
    con=db(); cur=con.execute("DELETE FROM accounts WHERE id=?",(account_id,)); con.commit(); return cur.rowcount>0

def decode_body(payload: dict) -> str:
    def walk(part):
        if part.get("mimeType")=="text/plain" and part.get("body",{}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]+"===").decode("utf-8","replace")
        for child in part.get("parts",[]):
            found=walk(child)
            if found:return found
        return ""
    return walk(payload)

def list_messages(account_id: str, limit: int=20) -> list[dict[str,Any]]:
    api=service(account_id); listing=api.users().messages().list(userId="me",labelIds=["INBOX"],maxResults=limit).execute()
    out=[]
    for item in listing.get("messages",[]):
        msg=api.users().messages().get(userId="me",id=item["id"],format="full").execute(); payload=msg["payload"]
        headers={h["name"].lower():h["value"] for h in payload.get("headers",[])}; body=decode_body(payload); text=(headers.get("subject","")+" "+body).lower()
        urgent=any(x in text for x in ["urgent","deadline","tomorrow","asap","interview"]); reply=any(x in text for x in ["please","could you","would you","confirm","?"])
        category="Urgent" if urgent else "Requires reply" if reply else "Newsletter" if "unsubscribe" in text else "Meeting" if any(x in text for x in ["meeting","calendar","call"]) else "Invoice" if any(x in text for x in ["invoice","payment","receipt"]) else "Follow-up"
        priority=min(98,35+(35 if urgent else 0)+(22 if reply else 0)+(8 if "UNREAD" in msg.get("labelIds",[]) else 0))
        sender=headers.get("from","Unknown sender"); sender_name=sender.split("<")[0].strip(' \"') or sender
        out.append({"id":msg["id"],"accountId":account_id,"threadId":msg["threadId"],"messageId":headers.get("message-id"),"sender":sender_name,"email":sender,"initials":"".join(x[0] for x in sender_name.split()[:2]).upper(),"subject":headers.get("subject","(No subject)"),"preview":msg.get("snippet",""),"body":body or msg.get("snippet",""),"receivedAt":headers.get("date",""),"relativeTime":"","category":category,"priority":priority,"unread":"UNREAD" in msg.get("labelIds",[]),"starred":"STARRED" in msg.get("labelIds",[]),"summary":msg.get("snippet","")+"…","actionRequired":"Review and reply" if reply else "No immediate action required","reason":"Urgency and direct-request signals found" if urgent or reply else "No direct request detected","attachments":[],"actionItems":[],"threadCount":1})
    return out

def send_reply(account_id: str, to: str, subject: str, body: str, thread_id: str|None=None, message_id: str|None=None):
    msg=EmailMessage(); msg.set_content(body); msg["To"]=to; msg["Subject"]=subject if subject.lower().startswith("re:") else f"Re: {subject}"
    if message_id: msg["In-Reply-To"]=message_id; msg["References"]=message_id
    raw=base64.urlsafe_b64encode(msg.as_bytes()).decode(); payload={"raw":raw}
    if thread_id: payload["threadId"]=thread_id
    return service(account_id).users().messages().send(userId="me",body=payload).execute()
