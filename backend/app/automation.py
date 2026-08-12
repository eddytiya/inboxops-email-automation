"""Background automation, durable notifications, retries, and run observability."""
from __future__ import annotations
import json, logging, os, threading, time
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from . import gmail, operations, smart_sections, workspace

log=logging.getLogger("inboxops.automation")
_stop=threading.Event(); _thread:threading.Thread|None=None

def _now()->str:return datetime.now(timezone.utc).isoformat()
def init_tables():
 con=gmail.db();con.executescript("""
 CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY,kind TEXT NOT NULL,title TEXT NOT NULL,body TEXT,account_id TEXT,thread_id TEXT,status TEXT DEFAULT 'unread',created_at TEXT NOT NULL,read_at TEXT);
 CREATE TABLE IF NOT EXISTS automation_runs(id TEXT PRIMARY KEY,job TEXT NOT NULL,status TEXT NOT NULL,started_at TEXT NOT NULL,finished_at TEXT,attempts INTEGER DEFAULT 0,details TEXT,error TEXT);
 CREATE TABLE IF NOT EXISTS sync_state(account_id TEXT PRIMARY KEY,last_sync_at TEXT,last_history_id TEXT,last_error TEXT);
 """);con.commit()
def notify(kind:str,title:str,body:str="",account_id:str|None=None,thread_id:str|None=None):
 init_tables();con=gmail.db();item={"id":str(uuid4()),"kind":kind,"title":title,"body":body,"account_id":account_id,"thread_id":thread_id,"status":"unread","created_at":_now()};con.execute("INSERT INTO notifications(id,kind,title,body,account_id,thread_id,status,created_at) VALUES(:id,:kind,:title,:body,:account_id,:thread_id,:status,:created_at)",item);con.commit();return item
def notifications(unread_only:bool=False):
 init_tables();sql="SELECT * FROM notifications"+(" WHERE status='unread'" if unread_only else "")+" ORDER BY created_at DESC LIMIT 200";return[dict(x)for x in gmail.db().execute(sql)]
def mark_read(notification_id:str):
 con=gmail.db();cur=con.execute("UPDATE notifications SET status='read',read_at=? WHERE id=?",(_now(),notification_id));con.commit();return cur.rowcount>0
def runs():init_tables();return[dict(x)for x in gmail.db().execute("SELECT * FROM automation_runs ORDER BY started_at DESC LIMIT 100")]
def _retry(name:str,fn,attempts:int=3):
 run_id=str(uuid4());init_tables();con=gmail.db();con.execute("INSERT INTO automation_runs(id,job,status,started_at) VALUES(?,?,?,?)",(run_id,name,"running",_now()));con.commit();last=None
 for attempt in range(1,attempts+1):
  try:
   result=fn();con.execute("UPDATE automation_runs SET status='success',finished_at=?,attempts=?,details=? WHERE id=?",(_now(),attempt,json.dumps(result,default=str)[:10000],run_id));con.commit();return result
  except Exception as exc:
   last=exc
   if attempt<attempts:time.sleep(min(2**(attempt-1),4))
 con.execute("UPDATE automation_runs SET status='failed',finished_at=?,attempts=?,error=? WHERE id=?",(_now(),attempts,str(last)[:2000],run_id));con.commit();log.exception("Automation job %s failed",name,exc_info=last);return {"error":str(last)}
def sync_account(account_id:str):
 page=operations.list_threads(account_id,limit=int(os.getenv("SYNC_MESSAGE_LIMIT","50")));count=0
 for item in page["items"]:
  thread=operations.get_thread(account_id,item["threadId"]);latest=thread["messages"][-1]
  workspace.upsert_document({"id":latest["id"],"account_id":account_id,"thread_id":latest["threadId"],"subject":latest["subject"],"sender":latest["from"],"body":latest["bodyText"],"received_at":latest["date"]});workspace.record_contact(latest["from"],latest["from"],latest["date"]);count+=1
 if os.getenv("AUTO_CLASSIFY","true").lower()=="true":smart_sections.sync(account_id,min(count,50))
 con=gmail.db();con.execute("INSERT INTO sync_state(account_id,last_sync_at,last_error) VALUES(?,?,NULL) ON CONFLICT(account_id) DO UPDATE SET last_sync_at=excluded.last_sync_at,last_error=NULL",(account_id,_now()));con.commit();return {"accountId":account_id,"synced":count}
def cycle():
 for account in gmail.accounts():_retry("inbox_sync",lambda account_id=account["id"]:sync_account(account_id))
 for reminder in operations.due_reminders():
  notify("reminder",reminder["title"],f"Due {reminder['remind_at']}",reminder.get("account_id"),reminder.get("thread_id"));operations.complete_reminder(reminder["id"])
 for followup in _retry("followup_check",operations.check_followups) or []:
  if isinstance(followup,dict) and followup.get("id"):notify("followup",f"Follow up: {followup.get('subject') or 'conversation'}",f"No reply by {followup['due_at']}",followup.get("account_id"),followup.get("thread_id"))
def _loop():
 while not _stop.is_set():
  _retry("automation_cycle",cycle,1);_stop.wait(max(30,int(os.getenv("AUTOMATION_INTERVAL_SECONDS","300"))))
def start():
 global _thread
 if os.getenv("AUTOMATION_ENABLED","true").lower()!="true" or (_thread and _thread.is_alive()):return
 _stop.clear();_thread=threading.Thread(target=_loop,name="inboxops-automation",daemon=True);_thread.start()
def stop():_stop.set()
def status():return {"enabled":os.getenv("AUTOMATION_ENABLED","true").lower()=="true","running":bool(_thread and _thread.is_alive()),"intervalSeconds":max(30,int(os.getenv("AUTOMATION_INTERVAL_SECONDS","300"))),"accounts":len(gmail.accounts()),"recentRuns":runs()[:10]}
def enable_gmail_watch(account_id:str):
 topic=os.getenv("GMAIL_PUBSUB_TOPIC")
 if not topic:raise RuntimeError("GMAIL_PUBSUB_TOPIC is not configured")
 result=gmail.service(account_id).users().watch(userId="me",body={"topicName":topic,"labelIds":["INBOX"]}).execute();con=gmail.db();con.execute("INSERT INTO sync_state(account_id,last_sync_at,last_history_id,last_error) VALUES(?,?,?,NULL) ON CONFLICT(account_id) DO UPDATE SET last_history_id=excluded.last_history_id,last_error=NULL",(account_id,_now(),result.get("historyId")));con.commit();return result
