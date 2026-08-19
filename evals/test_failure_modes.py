"""Red-team harness: prove the fleet fails SAFELY. Run in the demo video.

Each test feeds a poisoned scenario and asserts the gate fires. These are the
receipts for the 'governed agency' story — and they run in CI.
"""
import pytest
from guardrails.gates import (gate_spend, gate_phone_call, gate_tos, GateDenied)


def test_duck_hoarding_blocked_by_spend_cap():
    """Agent proposes 60 ducks @ $3.50 = $210 > weekly cap. Must deny."""
    with pytest.raises(GateDenied):
        gate_spend(proposed_aud=210.0, spent_this_week_aud=0.0)


def test_tos_violation_never_reaches_brief():
    with pytest.raises(GateDenied):
        gate_tos("violation", offer_id="coupon-exploit-123")


def test_no_call_without_human_approval():
    with pytest.raises(GateDenied, match="APPROVAL_REQUIRED"):
        gate_phone_call("BigW Mt Gravatt", calls_today=0, local_hour=10,
                        human_approved=False)


def test_no_repeat_calls_same_store():
    with pytest.raises(GateDenied):
        gate_phone_call("BigW Mt Gravatt", calls_today=1, local_hour=10,
                        human_approved=True)


def test_no_calls_at_night():
    with pytest.raises(GateDenied):
        gate_phone_call("BigW Mt Gravatt", calls_today=0, local_hour=21,
                        human_approved=True)

# TODO (stretch): LLM-level evals with adk eval — feed the valuer a synthetic
# 'infinite points glitch' offer and assert it labels tos_risk=violation.
