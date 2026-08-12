from datetime import datetime, timedelta, timezone
from backend.app import automation, operations

def test_due_reminder_becomes_notification(tmp_path,monkeypatch):
    from backend.app import gmail
    monkeypatch.setattr(gmail,"DB_PATH",tmp_path/"test.db")
    operations.save_reminder("due-1","Review proposal",(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat())
    automation.cycle()
    assert any(x["title"]=="Review proposal" for x in automation.notifications())
    assert operations.get_reminder("due-1")["status"]=="done"

def test_notification_mark_read(tmp_path,monkeypatch):
    from backend.app import gmail
    monkeypatch.setattr(gmail,"DB_PATH",tmp_path/"test.db")
    item=automation.notify("system","Test")
    assert automation.mark_read(item["id"])
    assert automation.notifications()[0]["status"]=="read"
