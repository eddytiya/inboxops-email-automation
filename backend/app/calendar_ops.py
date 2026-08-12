"""Narrowly-scoped Google Calendar operations; all writes require explicit UI approval."""
from __future__ import annotations
from googleapiclient.discovery import build
from .gmail import credentials, CALENDAR_SCOPES

def status(account_id:str)->dict:
 creds=credentials(account_id);granted=set(creds.scopes or [])
 return {"connected":all(s in granted for s in CALENDAR_SCOPES),"grantedScopes":sorted(granted & set(CALENDAR_SCOPES)),"requiredScopes":CALENDAR_SCOPES}
def service(account_id:str):
 if not status(account_id)["connected"]:raise PermissionError("Calendar permission is not connected for this account")
 return build("calendar","v3",credentials=credentials(account_id),cache_discovery=False)
def freebusy(account_id:str,time_min:str,time_max:str,time_zone:str="Asia/Kolkata"):
 return service(account_id).freebusy().query(body={"timeMin":time_min,"timeMax":time_max,"timeZone":time_zone,"items":[{"id":"primary"}]}).execute()
def create_event(account_id:str,event:dict):
 body={"summary":event["summary"],"description":event.get("description","Created with explicit approval in InboxOps"),"location":event.get("location"),"start":{"dateTime":event["start"],"timeZone":event.get("time_zone","Asia/Kolkata")},"end":{"dateTime":event["end"],"timeZone":event.get("time_zone","Asia/Kolkata")},"attendees":[{"email":x} for x in event.get("attendees",[])]}
 return service(account_id).events().insert(calendarId="primary",body=body,sendUpdates="all" if event.get("notify_attendees") else "none").execute()
