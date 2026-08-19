"""Governance layer. Every real-world action passes through here.

Design rule: the agent PROPOSES, gates DECIDE, humans APPROVE.
This is the layer the demo shows off — the refusal and the permission-ask.
"""
import json
import logging
from datetime import datetime, timezone
from config.settings import settings

audit = logging.getLogger("pointsduck.audit")  # -> Cloud Logging in prod


def _log(event: str, **kw):
    audit.info(json.dumps({"event": event, "ts": datetime.now(timezone.utc).isoformat(), **kw}))


class GateDenied(Exception):
    pass


def gate_spend(proposed_aud: float, spent_this_week_aud: float) -> None:
    if spent_this_week_aud + proposed_aud > settings.spend_cap_aud_per_week:
        _log("spend_denied", proposed=proposed_aud, spent=spent_this_week_aud)
        raise GateDenied(
            f"Weekly spend cap A${settings.spend_cap_aud_per_week} would be exceeded. "
            "Escalating to human instead of buying."
        )
    _log("spend_allowed", proposed=proposed_aud)


def gate_phone_call(store_name: str, calls_today: int, local_hour: int,
                    human_approved: bool) -> None:
    lo, hi = settings.call_window_local
    if not (lo <= local_hour < hi):
        _log("call_denied_hours", store=store_name, hour=local_hour)
        raise GateDenied("Outside calling hours. Queued for tomorrow.")
    if calls_today >= settings.max_calls_per_store_per_day:
        _log("call_denied_frequency", store=store_name)
        raise GateDenied("Already called this store today. Not harassing them.")
    if not human_approved:
        _log("call_needs_approval", store=store_name)
        raise GateDenied("APPROVAL_REQUIRED: ask the human before dialling.")
    _log("call_allowed", store=store_name)


def gate_tos(tos_risk: str, offer_id: str) -> None:
    if tos_risk == "violation":
        _log("tos_denied", offer=offer_id)
        raise GateDenied("Offer requires violating program T&Cs. Excluded from brief.")
    if tos_risk == "grey":
        _log("tos_flagged", offer=offer_id)
        # Grey-area stacks are shown but flagged, never auto-actioned.


CALL_SCRIPT_PREAMBLE = (
    "Hi, I'm an AI assistant calling on behalf of a customer. "
    "Just a quick stock question if you have a moment — "
)
