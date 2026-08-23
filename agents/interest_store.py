"""Potential-users (interest) store — a lightweight Firestore lead list.

Every signed-in user who tries the hosted onboarding is recorded here so the project can
understand demand and (with the user's explicit opt-in) follow up. Kept deliberately
separate from duckfleet_profiles: a profile is operating data the fleet reads; this is
product/CRM data the fleet never touches.

Privacy stance:
  - `note_visit` / `note_sample` record OPERATIONAL facts (this verified person used the
    service) — legitimate for running it.
  - `interested` is an EXPLICIT opt-in for "keep me posted" follow-up. We never email the
    list automatically; the only automated email is the on-demand sample, sent solely to
    the user's own verified address.
Best-effort (mirrors agents/history.py): failures are logged and swallowed.
Collection: `duckfleet_interest`, one doc per verified email.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from config.settings import settings

log = logging.getLogger("duckfleet.interest")

_COLLECTION = "duckfleet_interest"
_SAMPLE_COOLDOWN = timedelta(hours=24)


def _client():
    from google.cloud import firestore
    return firestore.Client(project=settings.project_id)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def note_visit(email: str) -> None:
    """Record that a verified user opened the app (first_seen once, last_seen every time)."""
    if not email:
        return
    try:
        ref = _client().collection(_COLLECTION).document(email)
        snap = ref.get()
        data = {"email": email, "last_seen": _now()}
        if not snap.exists:
            data["first_seen"] = _now()
        ref.set(data, merge=True)
    except Exception as e:  # noqa: BLE001
        log.warning("interest note_visit failed (%s)", e)


def note_sample(email: str) -> None:
    """Record that a sample brief was sent to this user (for rate-limiting + demand signal)."""
    if not email:
        return
    try:
        from google.cloud import firestore
        ref = _client().collection(_COLLECTION).document(email)
        ref.set({"email": email, "last_sample": _now(),
                 "sample_count": firestore.Increment(1)}, merge=True)
    except Exception as e:  # noqa: BLE001
        log.warning("interest note_sample failed (%s)", e)


def set_interested(email: str, interested: bool) -> bool:
    """Explicit opt-in flag for follow-up. Returns the stored value (best-effort)."""
    if not email:
        return False
    try:
        _client().collection(_COLLECTION).document(email).set(
            {"email": email, "interested": interested, "interested_ts": _now()}, merge=True)
        return interested
    except Exception as e:  # noqa: BLE001
        log.warning("interest set_interested failed (%s)", e)
        return False


def can_send_sample(email: str) -> bool:
    """Rate limit: at most one sample per user per 24h. Fails open only on read errors."""
    if not email:
        return False
    try:
        snap = _client().collection(_COLLECTION).document(email).get()
        last = (snap.to_dict() or {}).get("last_sample") if snap.exists else None
        if not last:
            return True
        return datetime.now(timezone.utc) - datetime.fromisoformat(last) >= _SAMPLE_COOLDOWN
    except Exception as e:  # noqa: BLE001
        log.warning("interest can_send_sample check failed (%s); allowing", e)
        return True
