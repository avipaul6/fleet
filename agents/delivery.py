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
from html import escape as _esc

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
    by_ref = _by_ref(result)
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
              f"   {top.reasoning}", *_links_text(top, by_ref), _DIV, ""]

    others = [a for a in items if a.verdict in ("do_it", "needs_approval") and a is not top]
    if others:
        L.append("✅ ALSO WORTH DOING")
        for a in others:
            cpp = f"  ·  {a.cents_per_point}c/pt" if a.cents_per_point is not None else ""
            L += [f"  • {a.headline} — ${a.net_value_aud:,.2f}{cpp}", f"    {a.reasoning}",
                  *_links_text(a, by_ref)]
        L.append("")

    skips = [a for a in items if a.verdict == "skip"]
    if skips:
        L.append("⛔ SKIPPED (saved you the trip)")
        for a in skips:
            L += [f"  • {a.headline}", f"    {a.reasoning}"]
        L.append("")

    if excluded:
        L += [f"\U0001F6AB EXCLUDED — {excluded} offer(s) blocked for ToS risk before review", ""]

    calls = result.get("call_candidates", [])
    if calls:
        L.append("\U0001F4DE STOCK CHECK — reply APPROVE and the fleet will call to verify before you go:")
        for c in calls:
            L.append(f"  • {c['merchant']} — {c['item']} (gated call: it self-identifies as AI)")
        L.append("")

    econ = result.get("economics")
    if econ:
        c, v, roi = econ.get("cost_aud", 0), econ.get("value_aud", 0), econ.get("roi")
        if econ.get("verdict") == "quiet_night":
            L += [f"\U0001F9EE Run economics: ~${c:.3f} compute · nothing cleared the bar — "
                  f"a quiet, cheap night (the fleet won't burn credit for nothing).", ""]
        else:
            roi_s = f"  (≈{roi:,.0f}× return)" if roi else ""
            worth = "worth running" if econ.get("verdict") == "worth_it" else "NOT worth the compute"
            L += [f"\U0001F9EE Run economics: ~${c:.3f} compute → ${v:,.2f} of value surfaced"
                  f"{roi_s} — {worth}.", ""]

    hist = result.get("history_rows", 0)
    L += [_SUB, "What's real vs simulated (build period):",
          f"  • Deals: {'replay fixtures (canned)' if mode == 'replay' else 'live OzBargain feed (real)'}",
          "  • Points maths & spend cap: real (deterministic Python)",
          f"  • Drive time/fuel: {'frozen fixture values' if mode == 'replay' else 'estimated from a local store directory'}",
          "  • Phone stock-check: gated; a real call on your approval (Twilio), else labelled-simulated",
          f"  • History → BigQuery: {f'yes ({hist} rows)' if hist else 'off'}",
          "", "Reply STOP to pause the fleet."]
    return "\n".join(L)


def _badge(verdict: str) -> str:
    c = {"do_it": ("#e6f4ea", "#1a7f37", "DO IT"),
         "needs_approval": ("#fef7e6", "#b54708", "NEEDS YOUR OK"),
         "skip": ("#fdecec", "#b42318", "SKIP")}.get(verdict, ("#eee", "#333", verdict.upper()))
    return (f'<span style="background:{c[0]};color:{c[1]};padding:2px 8px;border-radius:10px;'
            f'font-size:11px;font-weight:700">{c[2]}</span>')


def _calendar_url(title: str, details: str = "") -> str:
    """A Google Calendar 'add event' link (all-day, tomorrow) so a good one isn't forgotten."""
    from datetime import date, timedelta
    from urllib.parse import quote
    d0 = date.today() + timedelta(days=1)
    d1 = d0 + timedelta(days=1)
    return ("https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={quote('DuckFleet: ' + title)}&details={quote(details)}"
            f"&dates={d0:%Y%m%d}/{d1:%Y%m%d}")


def _by_ref(result: dict) -> dict:
    return {a.get("audit_ref"): a for a in result.get("assessed", [])}


def _links_html(item, by_ref: dict) -> str:
    url = (by_ref.get(item.audit_ref) or {}).get("source_url")
    btn = ("display:inline-block;padding:6px 12px;border-radius:8px;text-decoration:none;"
           "font-size:13px;font-weight:600;margin:8px 8px 0 0")
    out = []
    if url:
        out.append(f'<a href="{_esc(url)}" style="{btn};background:#1a7f37;color:#fff">Activate / view ↗</a>')
    out.append(f'<a href="{_esc(_calendar_url(item.headline))}" style="{btn};'
               f'background:#eef2ff;color:#3538cd">📅 Add reminder</a>')
    return "".join(out)


def _links_text(item, by_ref: dict) -> list[str]:
    url = (by_ref.get(item.audit_ref) or {}).get("source_url")
    lines = []
    if url:
        lines.append(f"   ↗ Activate/view: {url}")
    lines.append(f"   📅 Add reminder: {_calendar_url(item.headline)}")
    return lines


def render_html(result: dict) -> str:
    """Light, email-safe HTML (inline styles, tables, no images). Sent as the HTML
    alternative alongside the plain-text version — clients that block HTML fall back."""
    mode = result.get("mode", "live")
    items = sorted(result.get("brief", []), key=lambda a: a.rank)
    by_ref = _by_ref(result)
    excluded = result.get("excluded_tos", 0)
    top = next((a for a in items if a.verdict in ("do_it", "needs_approval")), None)
    others = [a for a in items if a.verdict in ("do_it", "needs_approval") and a is not top]
    skips = [a for a in items if a.verdict == "skip"]
    calls = result.get("call_candidates", [])
    econ = result.get("economics")
    banner = "SIMULATION · replay fixtures" if mode == "replay" else "LIVE · OzBargain feed"

    P = ['<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;'
         'max-width:640px;margin:0 auto;color:#1a1a1a;line-height:1.45">']
    P.append('<div style="font-size:22px;font-weight:800">🦆 DuckFleet — Daily Hunt</div>')
    P.append(f'<div style="color:#667085;font-size:13px;margin:2px 0 16px">'
             f'{date.today():%-d %b %Y} · {banner}</div>')

    if top:
        cpp = f' · {top.cents_per_point}c/pt' if top.cents_per_point is not None else ''
        P.append(
            '<div style="border:1px solid #e4e7ec;border-radius:12px;padding:16px;'
            'margin-bottom:16px;background:#fbfdff">'
            '<div style="font-size:11px;letter-spacing:.5px;color:#667085;font-weight:700">⭐ TOP PICK</div>'
            f'<div style="font-size:34px;font-weight:800;margin:4px 0">${top.net_value_aud:,.2f}'
            f'<span style="font-size:14px;font-weight:600;color:#667085"> net{cpp}</span></div>'
            f'<div style="font-weight:600;margin-bottom:6px">{_esc(top.headline)} &nbsp;{_badge(top.verdict)}</div>'
            f'<div style="color:#475467;font-size:14px">{_esc(top.reasoning)}</div>'
            f'<div>{_links_html(top, by_ref)}</div></div>')

    if others:
        P.append('<div style="font-weight:700;margin:14px 0 4px">✅ Also worth doing</div>')
        for a in others:
            P.append(f'<div style="border-top:1px solid #f0f0f0;padding:8px 0;font-size:14px">'
                     f'{_esc(a.headline)} — ${a.net_value_aud:,.0f} &nbsp;{_badge(a.verdict)}'
                     f'<div>{_links_html(a, by_ref)}</div></div>')

    if skips:
        lis = "".join(f'<li style="margin:5px 0"><span style="color:#344054">{_esc(a.headline)}</span>'
                      f' — <span style="color:#667085">{_esc(a.reasoning)}</span></li>' for a in skips)
        P.append('<div style="font-weight:700;margin:16px 0 4px">⛔ Skipped</div>'
                 f'<ul style="margin:0;padding-left:18px;font-size:14px">{lis}</ul>')

    if excluded:
        P.append(f'<div style="margin:12px 0;color:#b42318;font-size:14px">🚫 {excluded} offer(s) '
                 'excluded for ToS risk before review</div>')

    if calls:
        lis = "".join(f'<li style="margin:3px 0">{_esc(c["merchant"])} — {_esc(c["item"])}</li>' for c in calls)
        P.append('<div style="border:1px dashed #c9d2e3;border-radius:10px;padding:10px 14px;'
                 'margin:16px 0;background:#fafbff;font-size:14px"><b>📞 Stock check</b> — reply '
                 '<b>APPROVE</b> and the fleet will call to verify (it self-identifies as AI):'
                 f'<ul style="margin:6px 0 0;padding-left:18px">{lis}</ul></div>')

    if econ:
        c, v, roi = econ.get("cost_aud", 0), econ.get("value_aud", 0), econ.get("roi")
        if econ.get("verdict") == "quiet_night":
            etxt = f'🧮 ~${c:.3f} compute · nothing cleared the bar — a quiet, cheap night.'
        else:
            etxt = f'🧮 ~${c:.3f} compute → ${v:,.2f} value' + (f' (≈{roi:,.0f}× return)' if roi else '')
        P.append(f'<div style="margin:16px 0;font-size:13px;color:#475467">{etxt}</div>')

    P.append('<div style="border-top:1px solid #eee;margin-top:16px;padding-top:10px;'
             'color:#98a2b3;font-size:12px">Reply STOP to pause the fleet.</div></div>')
    return "".join(P)


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


def send_brief(subject: str, body_text: str, body_html: str | None = None) -> dict:
    """Send the brief to settings.notify_email as the configured sender. Sends
    multipart/alternative (plain text + optional HTML) so clients that block HTML fall
    back to plain text. Raises if Gmail isn't configured — gate on gmail_configured()."""
    if not gmail_configured():
        raise RuntimeError("Gmail not configured (set DUCKFLEET_GMAIL_* + DUCKFLEET_NOTIFY_EMAIL).")
    msg = EmailMessage()
    msg["To"] = settings.notify_email
    msg["From"] = settings.gmail_sender or "me"
    msg["Subject"] = subject
    msg.set_content(body_text)                      # plain-text fallback (always present)
    if body_html:
        msg.add_alternative(body_html, subtype="html")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    resp = httpx.post(_SEND_URL, headers={"Authorization": f"Bearer {_access_token()}"},
                      json={"raw": raw}, timeout=20.0)
    resp.raise_for_status()
    return resp.json()
