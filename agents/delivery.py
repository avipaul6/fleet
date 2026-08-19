"""Gmail delivery of the morning brief.

Credentials come ONLY from env / Secret Manager (never hardcoded, never committed):
DUCKFLEET_GMAIL_{SENDER,CLIENT_ID,CLIENT_SECRET,REFRESH_TOKEN} + DUCKFLEET_NOTIFY_EMAIL.
Runtime auth uses google-auth (already a dep) + httpx — no google-auth-oauthlib needed
here (that's only for the one-time scripts/gmail_authorize.py consent).
"""
from __future__ import annotations

import base64
from email.message import EmailMessage

import httpx
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from config.settings import settings

_TOKEN_URI = "https://oauth2.googleapis.com/token"
_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def gmail_configured() -> bool:
    """True only when every secret + recipient is present."""
    return bool(settings.gmail_client_id and settings.gmail_client_secret
                and settings.gmail_refresh_token and settings.notify_email)


def _access_token() -> str:
    creds = Credentials(
        token=None,
        refresh_token=settings.gmail_refresh_token,
        client_id=settings.gmail_client_id,
        client_secret=settings.gmail_client_secret,
        token_uri=_TOKEN_URI,
    )
    creds.refresh(Request())
    return creds.token


def send_brief(subject: str, body_text: str) -> dict:
    """Send the brief to settings.notify_email as the configured sender. Raises if
    Gmail isn't configured — callers should gate on gmail_configured() first."""
    if not gmail_configured():
        raise RuntimeError("Gmail not configured (set DUCKFLEET_GMAIL_* + DUCKFLEET_NOTIFY_EMAIL).")
    msg = EmailMessage()
    msg["To"] = settings.notify_email
    msg["From"] = settings.gmail_sender or "me"
    msg["Subject"] = subject
    msg.set_content(body_text)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    resp = httpx.post(_SEND_URL, headers={"Authorization": f"Bearer {_access_token()}"},
                      json={"raw": raw}, timeout=20.0)
    resp.raise_for_status()
    return resp.json()
