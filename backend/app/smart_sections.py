"""Local-first Gmail topic classification and label automation."""
from __future__ import annotations

import re
from typing import Any

from .gmail import service

SECTIONS: dict[str, dict[str, Any]] = {
    "sports": {
        "name": "Sports",
        "label": "InboxOps/Sports",
        "keywords": ["sports", "match", "fixture", "score", "tournament", "cricket", "football", "soccer", "ipl", "nba", "nfl", "fifa", "tennis", "formula 1", "f1", "championship", "league"],
        "domains": ["espn", "cricbuzz", "nba.com", "nfl.com", "fifa.com", "sports"],
    },
    "entertainment": {
        "name": "Entertainment",
        "label": "InboxOps/Entertainment",
        "keywords": ["movie", "series", "trailer", "concert", "streaming", "episode", "premiere", "music", "album", "artist", "cinema", "netflix", "spotify", "youtube", "prime video", "hotstar"],
        "domains": ["netflix", "spotify", "youtube", "primevideo", "hotstar", "imdb"],
    },
    "payments": {
        "name": "Payments",
        "label": "InboxOps/Payments",
        "keywords": ["payment", "paid", "invoice", "receipt", "transaction", "refund", "charged", "debit", "credit", "billing", "subscription", "renewal", "amount due", "bank", "upi", "card ending"],
        "domains": ["stripe", "paypal", "razorpay", "paytm", "phonepe", "bank", "billing"],
    },
    "jobs": {
        "name": "Jobs",
        "label": "InboxOps/Jobs",
        "keywords": ["job", "hiring", "recruiter", "interview", "application", "candidate", "career", "position", "role", "resume", "cv", "offer letter", "assessment", "opportunity"],
        "domains": ["linkedin", "indeed", "naukri", "glassdoor", "wellfound", "greenhouse", "lever.co", "workday"],
    },
    "news": {"name":"News","label":"InboxOps/News","keywords":["breaking news","headline","daily news","world news","politics","election","newsletter","top stories"],"domains":["reuters","bbc","cnn","nytimes","thehindu","indiatoday"]},
    "shopping": {"name":"Shopping","label":"InboxOps/Shopping","keywords":["order","shipped","delivery","cart","sale","discount","purchase","return"],"domains":["amazon","flipkart","myntra","ajio"]},
    "travel": {"name":"Travel","label":"InboxOps/Travel","keywords":["flight","hotel","booking","reservation","boarding pass","itinerary","trip","visa"],"domains":["airbnb","booking.com","makemytrip","indigo","airindia"]},
    "education": {"name":"Education","label":"InboxOps/Education","keywords":["course","class","assignment","exam","university","college","student","certificate"],"domains":["coursera","udemy","edx","unacademy"]},
    "social": {"name":"Social","label":"InboxOps/Social","keywords":["mentioned you","new follower","friend request","liked your","commented","connection request"],"domains":["instagram","facebook","x.com","twitter","linkedin"]},
    "promotions": {"name":"Promotions","label":"InboxOps/Promotions","keywords":["offer","coupon","deal","save up to","limited time","promo","clearance"],"domains":["marketing","offers","promotions"]},
    "finance": {"name":"Finance","label":"InboxOps/Finance","keywords":["bank statement","account balance","investment","mutual fund","stock","interest rate","tax"],"domains":["zerodha","groww","hdfcbank","icicibank","sbi"]},
    "security": {"name":"Security","label":"InboxOps/Security","keywords":["security alert","new login","password","verification code","otp","suspicious","two-factor"],"domains":["accounts.google","security","noreply"]},
    "health": {"name":"Health","label":"InboxOps/Health","keywords":["appointment","doctor","hospital","prescription","medical","health report","lab result"],"domains":["practo","apollohospitals","1mg"]},
    "food": {"name":"Food & Dining","label":"InboxOps/Food","keywords":["food order","restaurant","table reservation","menu","delivered","meal"],"domains":["swiggy","zomato","dominos"]},
    "events": {"name":"Events","label":"InboxOps/Events","keywords":["event","ticket","conference","webinar","workshop","registration","venue"],"domains":["eventbrite","bookmyshow","meetup"]},
    "support": {"name":"Support","label":"InboxOps/Support","keywords":["support ticket","case number","help request","customer support","resolved","technical issue"],"domains":["support","zendesk","freshdesk"]},
    "personal": {"name":"Personal","label":"InboxOps/Personal","keywords":["family","birthday","invitation","catch up","personal"],"domains":[]},
    "work": {"name":"Work","label":"InboxOps/Work","keywords":["project","client","deadline","deliverable","team update","review","proposal"],"domains":["slack","asana","notion"]},
    "government": {"name":"Government","label":"InboxOps/Government","keywords":["government","aadhaar","pan card","official notice","tax return","passport"],"domains":["gov.in","uidai","incometax"]},
    "subscriptions": {"name":"Subscriptions","label":"InboxOps/Subscriptions","keywords":["subscription","renewal","membership","plan expires","trial ends","unsubscribe"],"domains":[]},
}


def classify_message(message: dict[str, Any], selected: list[str] | None = None) -> dict[str, Any] | None:
    """Classify metadata locally and return the strongest topic above threshold."""
    sender = str(message.get("from", "")).lower()
    subject = str(message.get("subject", "")).lower()
    snippet = str(message.get("snippet", "")).lower()
    text = f"{sender} {subject} {snippet}"
    scores: dict[str, int] = {}
    reasons: dict[str, list[str]] = {}

    enabled = {key for key in (selected or SECTIONS.keys()) if key in SECTIONS}
    if not enabled:
        return None
    for key, section in SECTIONS.items():
        if key not in enabled:
            continue
        score = 0
        matched: list[str] = []
        for domain in section["domains"]:
            if domain in sender:
                score += 4
                matched.append(f"sender:{domain}")
        for keyword in section["keywords"]:
            if re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text):
                score += 2 if keyword in subject else 1
                matched.append(keyword)
        scores[key] = score
        reasons[key] = matched

    topic = max(scores, key=scores.get)
    score = scores[topic]
    if score < 2:
        return None
    confidence = min(0.98, 0.55 + score * 0.07)
    return {"topic": topic, "confidence": round(confidence, 2), "reason": ", ".join(reasons[topic][:4])}


def ensure_labels(account_id: str, selected: list[str] | None = None) -> dict[str, str]:
    api = service(account_id)
    existing = api.users().labels().list(userId="me").execute().get("labels", [])
    by_name = {item["name"]: item["id"] for item in existing}
    result: dict[str, str] = {}
    enabled = {key for key in (selected or SECTIONS.keys()) if key in SECTIONS}
    for key, section in SECTIONS.items():
        if key not in enabled:
            continue
        label_id = by_name.get(section["label"])
        if not label_id:
            created = api.users().labels().create(
                userId="me",
                body={
                    "name": section["label"],
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            ).execute()
            label_id = created["id"]
        result[key] = label_id
    return result


def overview(account_id: str, selected: list[str] | None = None) -> list[dict[str, Any]]:
    api = service(account_id)
    existing = api.users().labels().list(userId="me").execute().get("labels", [])
    by_name = {item["name"]: item["id"] for item in existing}
    sections = []
    enabled = {key for key in (selected or SECTIONS.keys()) if key in SECTIONS}
    for key, section in SECTIONS.items():
        if key not in enabled:
            continue
        label_id = by_name.get(section["label"])
        count = 0
        if label_id:
            count = api.users().threads().list(userId="me", labelIds=[label_id], maxResults=1).execute().get("resultSizeEstimate", 0)
        sections.append({"id": key, "name": section["name"], "gmailLabel": section["label"], "labelId": label_id, "count": count})
    return sections


def sync(account_id: str, limit: int = 50, selected: list[str] | None = None) -> dict[str, Any]:
    api = service(account_id)
    enabled = [key for key in (selected or SECTIONS.keys()) if key in SECTIONS]
    label_ids = ensure_labels(account_id, enabled)
    topic_label_ids = set(label_ids.values())
    listing = api.users().threads().list(userId="me", labelIds=["INBOX"], maxResults=min(max(limit, 1), 100)).execute()
    assignments = []

    for item in listing.get("threads", []):
        raw = api.users().threads().get(
            userId="me",
            id=item["id"],
            format="metadata",
            metadataHeaders=["From", "Subject"],
        ).execute()
        latest = raw.get("messages", [])[-1]
        headers = {header["name"].lower(): header["value"] for header in latest.get("payload", {}).get("headers", [])}
        candidate = {
            "from": headers.get("from", ""),
            "subject": headers.get("subject", ""),
            "snippet": latest.get("snippet", ""),
        }
        classification = classify_message(candidate, enabled)
        current = set(latest.get("labelIds", []))
        current_topics = current.intersection(topic_label_ids)
        if not classification:
            continue
        topic = classification["topic"]
        target_label = label_ids[topic]
        remove = list(current_topics - {target_label})
        if target_label not in current or remove:
            api.users().threads().modify(
                userId="me",
                id=item["id"],
                body={"addLabelIds": [target_label], "removeLabelIds": remove},
            ).execute()
        assignments.append({
            "threadId": item["id"],
            "topic": topic,
            "labelId": target_label,
            "confidence": classification["confidence"],
            "reason": classification["reason"],
        })

    return {"classified": len(assignments), "assignments": assignments, "sections": overview(account_id, enabled), "localOnly": True}
