"""Local-first privacy, search, tasks, contacts, and personalization services."""
from __future__ import annotations
import hashlib, json, math, re
from collections import Counter
from datetime import datetime, timezone
from uuid import uuid4
from .gmail import db

DEFAULT_PRIVACY={"hosted_ai_enabled":True,"redact_pii":True,"allow_accounts":[],"retain_ai_results":False,"attachment_ai_enabled":False}
PII_PATTERNS={
 "email":re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I),
 "phone":re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)"),
 "card":re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
 "government_id":re.compile(r"\b[A-Z]{2,5}[ -]?\d{5,12}\b",re.I),
 "amount":re.compile(r"(?:₹|\$|€|£)\s?[\d,]+(?:\.\d{2})?"),
}
def init_tables():
 con=db();con.executescript("""
 CREATE TABLE IF NOT EXISTS privacy_settings(id INTEGER PRIMARY KEY CHECK(id=1), settings TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS ai_audit(id TEXT PRIMARY KEY, account_id TEXT, action TEXT NOT NULL, provider TEXT, pii_redacted INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
 CREATE TABLE IF NOT EXISTS search_documents(id TEXT PRIMARY KEY, account_id TEXT NOT NULL, thread_id TEXT NOT NULL, subject TEXT, sender TEXT, body TEXT, received_at TEXT, UNIQUE(account_id,id));
 CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(id UNINDEXED,subject,sender,body,content='search_documents',content_rowid='rowid');
 CREATE TRIGGER IF NOT EXISTS search_ai AFTER INSERT ON search_documents BEGIN INSERT INTO search_fts(rowid,id,subject,sender,body) VALUES(new.rowid,new.id,new.subject,new.sender,new.body); END;
 CREATE TRIGGER IF NOT EXISTS search_ad AFTER DELETE ON search_documents BEGIN INSERT INTO search_fts(search_fts,rowid,id,subject,sender,body) VALUES('delete',old.rowid,old.id,old.subject,old.sender,old.body); END;
 CREATE TRIGGER IF NOT EXISTS search_au AFTER UPDATE ON search_documents BEGIN INSERT INTO search_fts(search_fts,rowid,id,subject,sender,body) VALUES('delete',old.rowid,old.id,old.subject,old.sender,old.body); INSERT INTO search_fts(rowid,id,subject,sender,body) VALUES(new.rowid,new.id,new.subject,new.sender,new.body); END;
 CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,title TEXT NOT NULL,notes TEXT,status TEXT DEFAULT 'pending',priority INTEGER DEFAULT 50,due_at TEXT,account_id TEXT,thread_id TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,completed_at TEXT);
 CREATE TABLE IF NOT EXISTS contacts(email TEXT PRIMARY KEY,name TEXT,message_count INTEGER DEFAULT 0,reply_count INTEGER DEFAULT 0,importance INTEGER DEFAULT 25,last_contact_at TEXT,vip INTEGER DEFAULT 0,notes TEXT);
 CREATE TABLE IF NOT EXISTS writing_profiles(account_id TEXT PRIMARY KEY,signature TEXT,tone TEXT DEFAULT 'Professional',preferences TEXT DEFAULT '{}',samples_accepted INTEGER DEFAULT 0);
 """);row=con.execute("SELECT 1 FROM privacy_settings WHERE id=1").fetchone()
 if not row:con.execute("INSERT INTO privacy_settings(id,settings) VALUES(1,?)",(json.dumps(DEFAULT_PRIVACY),))
 con.commit()

def privacy()->dict:init_tables();return json.loads(db().execute("SELECT settings FROM privacy_settings WHERE id=1").fetchone()[0])
def save_privacy(settings:dict)->dict:
 merged={**DEFAULT_PRIVACY,**settings};con=db();init_tables();con.execute("UPDATE privacy_settings SET settings=? WHERE id=1",(json.dumps(merged),));con.commit();return merged
def redact(text:str)->tuple[str,list[str]]:
 found=[]
 for name,pattern in PII_PATTERNS.items():
  if pattern.search(text):found.append(name);text=pattern.sub(f"[REDACTED_{name.upper()}]",text)
 return text,found
def prepare_ai(account_id:str,subject:str,body:str,action:str)->tuple[str,str,dict]:
 settings=privacy();allowed=settings["hosted_ai_enabled"] and (not settings["allow_accounts"] or account_id in settings["allow_accounts"])
 if not allowed:return subject,body,{"hostedAllowed":False,"redacted":False,"types":[]}
 types=[]
 if settings["redact_pii"]:
  subject,a=redact(subject);body,b=redact(body);types=sorted(set(a+b))
 return subject,body,{"hostedAllowed":True,"redacted":bool(types),"types":types}
def audit(account_id:str,action:str,provider:str|None,redacted:bool):
 init_tables();con=db();con.execute("INSERT INTO ai_audit(id,account_id,action,provider,pii_redacted) VALUES(?,?,?,?,?)",(str(uuid4()),account_id,action,provider,int(redacted)));con.commit()
def audits()->list[dict]:init_tables();return[dict(x)for x in db().execute("SELECT * FROM ai_audit ORDER BY created_at DESC LIMIT 100")]

def upsert_document(doc:dict):
 init_tables();con=db();con.execute("INSERT INTO search_documents(id,account_id,thread_id,subject,sender,body,received_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(account_id,id) DO UPDATE SET subject=excluded.subject,sender=excluded.sender,body=excluded.body,received_at=excluded.received_at",(doc["id"],doc["account_id"],doc["thread_id"],doc.get("subject"),doc.get("sender"),doc.get("body"),doc.get("received_at")));con.commit()
def search(query:str,account_id:str|None=None,limit:int=30)->list[dict]:
 init_tables();words=re.findall(r"[a-zA-Z0-9]{2,}",query.lower());synonyms={"invoice":["payment","receipt","bill"],"job":["interview","recruiter","application"],"meeting":["call","schedule","calendar"],"urgent":["asap","deadline","today"],"unresolved":["follow up","waiting","reply"]}
 expanded=words+[s for w in words for s in synonyms.get(w,[])];fts=" OR ".join(f'"{w}"' for w in expanded) or '""';params=[fts]
 sql="SELECT d.*,bm25(search_fts) rank FROM search_fts JOIN search_documents d ON d.rowid=search_fts.rowid WHERE search_fts MATCH ?"
 if account_id:sql+=" AND d.account_id=?";params.append(account_id)
 sql+=" ORDER BY rank LIMIT ?";params.append(limit)
 try:return[dict(x)for x in db().execute(sql,params)]
 except:return[]

def create_task(data:dict)->dict:
 init_tables();item={"id":str(uuid4()),**data};con=db();con.execute("INSERT INTO tasks(id,title,notes,status,priority,due_at,account_id,thread_id) VALUES(?,?,?,?,?,?,?,?)",(item["id"],item["title"],item.get("notes"),item.get("status","pending"),item.get("priority",50),item.get("due_at"),item.get("account_id"),item.get("thread_id")));con.commit();return dict(con.execute("SELECT * FROM tasks WHERE id=?",(item["id"],)).fetchone())
def tasks()->list[dict]:init_tables();return[dict(x)for x in db().execute("SELECT * FROM tasks ORDER BY status,priority DESC,due_at")]
def update_task(task_id:str,data:dict)->dict:
 init_tables();allowed={k:v for k,v in data.items() if k in {"title","notes","status","priority","due_at"}};con=db()
 for k,v in allowed.items():con.execute(f"UPDATE tasks SET {k}=? WHERE id=?",(v,task_id))
 if data.get("status")=="done":con.execute("UPDATE tasks SET completed_at=? WHERE id=?",(datetime.now(timezone.utc).isoformat(),task_id))
 con.commit();row=con.execute("SELECT * FROM tasks WHERE id=?",(task_id,)).fetchone();return dict(row) if row else {}

def record_contact(email:str,name:str,date:str|None=None):
 init_tables();con=db();con.execute("INSERT INTO contacts(email,name,message_count,importance,last_contact_at) VALUES(?,?,1,30,?) ON CONFLICT(email) DO UPDATE SET name=excluded.name,message_count=message_count+1,last_contact_at=excluded.last_contact_at,importance=MIN(100,25+(message_count+1)*3+vip*30)",(email.lower(),name,date));con.commit()
def contacts()->list[dict]:init_tables();return[dict(x)for x in db().execute("SELECT * FROM contacts ORDER BY importance DESC,message_count DESC")]
def update_contact(email:str,data:dict)->dict:
 con=db();init_tables()
 for k in("vip","notes","importance"):
  if k in data:con.execute(f"UPDATE contacts SET {k}=? WHERE email=?",(data[k],email.lower()))
 con.commit();row=con.execute("SELECT * FROM contacts WHERE email=?",(email.lower(),)).fetchone();return dict(row) if row else {}
def profile(account_id:str)->dict:
 init_tables();row=db().execute("SELECT * FROM writing_profiles WHERE account_id=?",(account_id,)).fetchone();return dict(row) if row else {"account_id":account_id,"signature":"Best,\nAditya","tone":"Professional","preferences":"{}","samples_accepted":0}
def save_profile(account_id:str,data:dict)->dict:
 init_tables();con=db();current=profile(account_id);con.execute("INSERT INTO writing_profiles(account_id,signature,tone,preferences,samples_accepted) VALUES(?,?,?,?,?) ON CONFLICT(account_id) DO UPDATE SET signature=excluded.signature,tone=excluded.tone,preferences=excluded.preferences,samples_accepted=excluded.samples_accepted",(account_id,data.get("signature",current["signature"]),data.get("tone",current["tone"]),json.dumps(data.get("preferences",json.loads(current["preferences"]))),data.get("samples_accepted",current["samples_accepted"])));con.commit();return profile(account_id)
