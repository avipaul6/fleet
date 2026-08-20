"""Red-team harness: prove the fleet fails SAFELY. Run in the demo video.

Each test feeds a poisoned scenario and asserts the gate fires. These are the
receipts for the 'governed agency' story — and they run in CI.
"""
import pytest
from guardrails.gates import (gate_spend, gate_phone_call, gate_tos, gate_call_script,
                              gate_preference, GateDenied, audit_trail, clear_audit,
                              CALL_SCRIPT_PREAMBLE)
from agents.valuer import compute_stack_value
from agents.worth_it import worth_it_verdict


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


# --- allowed / happy paths: governance must not block the good stuff ---

def test_spend_under_cap_allowed():
    gate_spend(proposed_aud=70.0, spent_this_week_aud=0.0)  # $70 < $100 cap → no raise


def test_call_allowed_on_happy_path():
    gate_phone_call("BigW Mt Gravatt", calls_today=0, local_hour=10, human_approved=True)


def test_grey_tos_flagged_not_blocked():
    """Grey-area stacks are shown-but-flagged, never auto-blocked (nor auto-actioned)."""
    gate_tos("grey", offer_id="gift-card-stack")  # must NOT raise
    assert any(r["event"] == "tos_flagged" for r in audit_trail())


# --- AI self-identification on calls is non-negotiable ---

def test_ai_self_identification_enforced():
    with pytest.raises(GateDenied):
        gate_call_script("Hey, do you have stock?")  # missing the required AI preamble


def test_ai_self_identification_passes_with_preamble():
    gate_call_script(CALL_SCRIPT_PREAMBLE + "do you have the duck in stock?")  # no raise


# --- governance-as-feature: worth-it refuses a bad errand, approves a good one ---

def test_worth_it_refuses_bad_errand():
    v = worth_it_verdict(net_value_aud=6.0, minutes=72.0, km=68.7)
    assert v["verdict"] == "skip" and v["net_after_trip_aud"] < 0


def test_worth_it_approves_good_errand():
    v = worth_it_verdict(net_value_aud=204.40, minutes=27.4, km=15.8)
    assert v["verdict"] == "do_it"


# --- demo numbers must be CORRECT: python does the maths, not the model ---

def test_hero_duck_math_is_correct():
    r = compute_stack_value(price_aud=3.50, points_out=30, program="qantas_ff",
                            multipliers=[10.0, 2.0])
    assert r["total_points"] == 600
    assert r["cost_cents_per_point"] == 0.58
    assert r["net_value_aud"] == 7.30


# --- receipts: denials land in the audit trail with ref + timestamp ---

def test_audit_trail_records_denials():
    clear_audit()
    with pytest.raises(GateDenied):
        gate_spend(proposed_aud=210.0, spent_this_week_aud=0.0)
    trail = audit_trail()
    assert any(r["event"] == "spend_denied" for r in trail)
    assert all("ref" in r and "ts" in r for r in trail)


# --- user preferences: skip what they don't want, respect conditional bars ---

def test_preference_avoids_unwanted_category():
    reason = gate_preference("credit_card", 1620.0)  # high value, but avoided
    assert reason is not None and "credit card" in reason


def test_preference_conditional_below_bar_is_skipped():
    assert gate_preference("insurance", 200.0) is not None   # below the $300 bar


def test_preference_conditional_above_bar_surfaces():
    assert gate_preference("insurance", 450.0) is None       # clears the $300 bar


def test_preference_allows_wanted_category():
    assert gate_preference("energy", 50.0) is None           # not avoided, not gated


# TODO (stretch): LLM-level evals with `adk eval` — feed the valuer a synthetic
# 'infinite points glitch' offer and assert it labels tos_risk=violation.
