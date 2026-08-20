"""Caller: gated voice stock-verification. STRONG model tier.

Escalation logic: only fires when online stock data is stale/unknown AND the
offer survived the worth-it gate AND the human approved. Voice path is
GCP-native: Conversational Agents (Dialogflow CX) Phone Gateway; the ADK agent
composes the question and consumes the transcript.

Demo note: this is your cinematic beat. One store, one call, agent identifies
itself as AI, gets an answer, hangs up politely.
"""
from google.adk.agents import Agent
from agents import model_factory
from agents.verification import run_verification_call
from guardrails.gates import record


def request_human_approval(store_name: str, reason: str) -> dict:
    """Tool: record an approval request for a call (prod: a Firestore doc the UI taps).
    The agent MUST call this first; the human's decision feeds place_verification_call."""
    ref = record("approval_requested", store=store_name, reason=reason)
    return {"status": "APPROVAL_REQUIRED", "store": store_name,
            "reason": reason, "audit_ref": ref}


def place_verification_call(store_name: str, item: str, human_approved: bool = False,
                            calls_today: int = 0, local_hour: int | None = None) -> dict:
    """Tool: place the GATED verification call. Delegates to the deterministic gated
    flow (calling hours + one-call-per-store + human approval + AI self-identification);
    synthesizes real audio and returns the (labelled-simulated) transcript. A refusal
    is a correct outcome."""
    return run_verification_call(store_name, item, human_approved,
                                 calls_today=calls_today, local_hour=local_hour)


caller = Agent(
    name="caller",
    model=model_factory.strong(),
    instruction="""You verify stock by phone ONLY when:
- online stock state is 'unknown' or last_verified > 48h, AND
- the offer's worth-it verdict is do_it, AND
- request_human_approval returned approved=true.
One question, polite, under 30 seconds of their time. Always begin with the
self-identification preamble. If any gate denies, record why and move on —
a denied call is a correct outcome, not a failure.""",
    tools=[request_human_approval, place_verification_call],
    output_key="call_results",
)
