"""Production hardening switches without disrupting localhost development."""
from __future__ import annotations
import os, secrets
from pathlib import Path
from fastapi import Request
from fastapi.responses import JSONResponse

ROOT=Path(__file__).resolve().parents[1];AUTH_KEY_PATH=ROOT/"secrets"/".app-auth-key"
def auth_key()->str:
 AUTH_KEY_PATH.parent.mkdir(parents=True,exist_ok=True)
 if not AUTH_KEY_PATH.exists():AUTH_KEY_PATH.write_text(secrets.token_urlsafe(48),encoding="utf-8")
 return AUTH_KEY_PATH.read_text(encoding="utf-8").strip()
async def auth_middleware(request:Request,call_next):
 required=os.getenv("INBOXOPS_ENV","development")=="production" or os.getenv("INBOXOPS_REQUIRE_AUTH","false").lower()=="true"
 if not required or request.url.path in {"/api/health","/api/auth/google/callback"} or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
  return await call_next(request)
 supplied=request.headers.get("Authorization","").removeprefix("Bearer ")
 if not secrets.compare_digest(supplied,auth_key()):return JSONResponse({"detail":"Authentication required"},status_code=401)
 return await call_next(request)
def readiness()->dict:
 production=os.getenv("INBOXOPS_ENV","development")=="production";checks={"httpsRedirect":os.getenv("GOOGLE_REDIRECT_URI","").startswith("https://"),"applicationAuth":production or os.getenv("INBOXOPS_REQUIRE_AUTH","false").lower()=="true","managedDatabase":bool(os.getenv("DATABASE_URL")),"managedEncryptionKey":bool(os.getenv("TOKEN_ENCRYPTION_KEY")),"secureCookie":os.getenv("SESSION_COOKIE_SECURE","false").lower()=="true"}
 return {"environment":"production" if production else "development","ready":all(checks.values()) if production else True,"checks":checks,"notes":"Local SQLite remains active; set DATABASE_URL and run a PostgreSQL migration before public deployment."}
