"""Onboarding agent — a conversation that builds the household profile.

Natural language in, validated profile.json out (the fleet reads it on the next run).
This is the agent-native alternative to a settings form, and the seed of a Claude/Gemini
managed agent for non-technical users. Chat with it via `adk web adk_apps` (app: onboarding).
"""
import json
from pathlib import Path

from google.adk.agents import Agent
from agents import model_factory
from schemas.profile import Profile
from guardrails.gates import record

_PROFILE_PATH = Path(__file__).resolve().parent.parent / "profile.json"


def save_profile(programs: list[str], avoid_categories: list[str],
                 conditional_categories: list[str], conditional_min_net_aud: float = 300.0,
                 spend_cap_aud_per_week: float = 100.0, notify_email: str = "",
                 home_label: str = "") -> dict:
    """Tool: persist the confirmed profile to profile.json (the fleet reads it next run).
    Maps free-form intent to the fleet's contract. Call once details are confirmed."""
    profile = Profile(
        programs=programs or [],
        prefs_avoid=avoid_categories or [],
        prefs_conditional={c: conditional_min_net_aud for c in (conditional_categories or [])},
        spend_cap_aud_per_week=spend_cap_aud_per_week,
        notify_email=notify_email or None,
        home_label=home_label or None,
    )
    _PROFILE_PATH.write_text(json.dumps(profile.model_dump(), indent=2))
    record("profile_saved", programs=profile.programs, avoid=profile.prefs_avoid)
    return {"status": "saved", "path": str(_PROFILE_PATH), "profile": profile.model_dump()}


onboarding = Agent(
    name="onboarding",
    model=model_factory.fast(),
    instruction="""You are DuckFleet's onboarding assistant. DuckFleet hunts loyalty-point
deals overnight and emails a ranked morning brief. In a friendly, BRIEF chat, learn the
user's profile, then call save_profile.

Accept free-form answers (e.g. "Qantas and Flybuys, no more credit cards, I'd switch
electricity or NBN for good points, $100 a week, brief to me@x.com"). Map them:
- programs -> qantas_ff | velocity | flybuys | everyday_rewards
- avoid_categories (NEVER show) -> credit_card | insurance | energy | telco | groceries |
  subscription | collectible | shopping | other   ("no more cards" -> credit_card)
- conditional_categories (show only if exceptional) + conditional_min_net_aud (default 300)
  ("health insurance only if it's really good" -> insurance)
- spend_cap_aud_per_week (default 100), notify_email, home_label (their suburb/postcode)
Things they're OPEN to (e.g. switching electricity/NBN) are neither avoid nor conditional —
leave them out; the fleet surfaces them by default.

Ask only for what's missing, confirm what you understood in ONE short line, then call
save_profile. After saving, tell them they're set and can preview a brief.""",
    tools=[save_profile],
    output_key="onboarding_result",
)
