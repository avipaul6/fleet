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
from guardrails.gates import (gate_phone_call, gate_call_script,
                              CALL_SCRIPT_PREAMBLE, GateDenied)


def request_human_approval(store_name: str, reason: str) -> dict:
    """Tool: push an approval request (demo: CLI prompt / Firestore doc the UI
    polls). Returns {'approved': bool}. The agent MUST call this first."""
    raise NotImplementedError


def place_verification_call(phone: str, question: str) -> dict:
    """Tool: trigger outbound call via Conversational Agents Phone Gateway,
    return transcript + extracted answer. Question MUST start with
    CALL_SCRIPT_PREAMBLE (AI self-identification is non-negotiable)."""
    gate_call_script(question)  # governed: enforces AI self-identification
    raise NotImplementedError  # TODO: Dialogflow CX Phone Gateway (deferred)


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
