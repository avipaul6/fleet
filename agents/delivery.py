"""Gmail delivery of the morning brief.

Credentials come ONLY from env / Secret Manager (never hardcoded, never committed):
DUCKFLEET_GMAIL_{SENDER,CLIENT_ID,CLIENT_SECRET,REFRESH_TOKEN} + DUCKFLEET_NOTIFY_EMAIL.
Runtime auth uses google-auth (already a dep) + httpx — no google-auth-oauthlib needed
here (that's only for the one-time scripts/gmail_authorize.py consent).
"""
from __future__ import annotations

import base64
from datetime import date
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


_DIV = "═" * 32   # heavy divider
_SUB = "─" * 32   # light divider


def _verdict_label(v: str) -> str:
    return {"do_it": "DO IT", "needs_approval": "NEEDS YOUR OK", "skip": "SKIP"}.get(v, v.upper())


def render_text(result: dict) -> str:
    """Readable plain-text brief (no HTML). Groups a highlighted top pick, other
    do-items, skips, and ToS exclusions, then a provenance block so — during the
    build/simulation period — it's clear what's real vs simulated."""
    mode = result.get("mode", "live")
    items = sorted(result.get("brief", []), key=lambda a: a.rank)
    excluded = result.get("excluded_tos", 0)
    n_do = sum(1 for a in items if a.verdict in ("do_it", "needs_approval"))
    n_skip = sum(1 for a in items if a.verdict == "skip")

    L: list[str] = [f"\U0001F986 DuckFleet — Daily Hunt · {date.today():%-d %b %Y}"]
    L.append("⚙️  SIMULATION MODE — replay fixtures (not live deals)"
             if mode == "replay" else "\U0001F4E1 LIVE run — OzBargain feed")
    L.append(f"Reviewed {result.get('n_candidates', len(items))}  ·  "
             f"{n_do} to do  ·  {n_skip} skipped  ·  {excluded} excluded (ToS)")
    L.append("")

    top = next((a for a in items if a.verdict in ("do_it", "needs_approval")), None)
    if top:
        cpp = f"  ·  {top.cents_per_point}c/pt" if top.cents_per_point is not None else ""
        L += [_DIV, "⭐ TOP PICK", top.headline,
              f"   Worth ${top.net_value_aud:,.2f}{cpp}   →  {_verdict_label(top.verdict)}",
              f"   {top.reasoning}", _DIV, ""]

    others = [a for a in items if a.verdict in ("do_it", "needs_approval") and a is not top]
    if others:
        L.append("✅ ALSO WORTH DOING")
        for a in others:
            cpp = f"  ·  {a.cents_per_point}c/pt" if a.cents_per_point is not None else ""
            L += [f"  • {a.headline} — ${a.net_value_aud:,.2f}{cpp}", f"    {a.reasoning}"]
        L.append("")

    skips = [a for a in items if a.verdict == "skip"]
    if skips:
        L.append("⛔ SKIPPED (saved you the trip)")
        for a in skips:
            L += [f"  • {a.headline}", f"    {a.reasoning}"]
        L.append("")

    if excluded:
        L += [f"\U0001F6AB EXCLUDED — {excluded} offer(s) blocked for ToS risk before review", ""]

    hist = result.get("history_rows", 0)
    L += [_SUB, "What's real vs simulated (build period):",
          f"  • Deals: {'replay fixtures (canned)' if mode == 'replay' else 'live OzBargain feed (real)'}",
          "  • Points maths & spend cap: real (deterministic Python)",
          f"  • Drive time/fuel: {'frozen fixture values' if mode == 'replay' else 'estimated from a local store directory'}",
          "  • Phone stock-check: not enabled yet (would be gated + labelled)",
          f"  • History → BigQuery: {f'yes ({hist} rows)' if hist else 'off'}",
          "", "Reply STOP to pause the fleet."]
    return "\n".join(L)


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
