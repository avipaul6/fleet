"""Onboarding agent — a conversation that builds the household profile.

Natural language in, validated profile out. Two surfaces share this one brain:
  - local dev: `adk web adk_apps` (app: onboarding) — the `onboarding` agent below,
    whose save tool writes profile.json.
  - hosted product: the Cloud Run onboarding page (runtimes/gcp_adk/onboard_service.py)
    builds an agent via `build_onboarding_agent()` with a save tool that writes to Firestore.
The mapping/logic lives here (runtime-agnostic); only the persistence target differs.
"""
import json
from pathlib import Path

from google.adk.agents import Agent
from agents import model_factory
from schemas.profile import Profile
from guardrails.gates import record

_PROFILE_PATH = Path(__file__).resolve().parent.parent / "profile.json"

INSTRUCTION = """You are DuckFleet's onboarding assistant. DuckFleet hunts loyalty-point
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
save_profile. After saving, tell them they're set and the fleet will hunt for them tonight."""


def build_profile(programs: list[str], avoid_categories: list[str],
                  conditional_categories: list[str], conditional_min_net_aud: float = 300.0,
                  spend_cap_aud_per_week: float = 100.0, notify_email: str = "",
                  home_label: str = "") -> Profile:
    """Map free-form onboarding intent onto the fleet's Profile contract. Pure — no I/O."""
    return Profile(
        programs=programs or [],
        prefs_avoid=avoid_categories or [],
        prefs_conditional={c: conditional_min_net_aud for c in (conditional_categories or [])},
        spend_cap_aud_per_week=spend_cap_aud_per_week,
        notify_email=notify_email or None,
        home_label=home_label or None,
    )


def save_profile(programs: list[str], avoid_categories: list[str],
                 conditional_categories: list[str], conditional_min_net_aud: float = 300.0,
                 spend_cap_aud_per_week: float = 100.0, notify_email: str = "",
                 home_label: str = "") -> dict:
    """Tool: persist the confirmed profile to profile.json (the fleet reads it next run).
    Maps free-form intent to the fleet's contract. Call once details are confirmed."""
    profile = build_profile(programs, avoid_categories, conditional_categories,
                            conditional_min_net_aud, spend_cap_aud_per_week,
                            notify_email, home_label)
    _PROFILE_PATH.write_text(json.dumps(profile.model_dump(), indent=2))
    record("profile_saved", programs=profile.programs, avoid=profile.prefs_avoid)
    return {"status": "saved", "path": str(_PROFILE_PATH), "profile": profile.model_dump()}


def build_onboarding_agent(save_tool) -> Agent:
    """Construct the onboarding agent with a caller-supplied save tool.

    `save_tool` must be a callable with the same signature as `save_profile` and named
    `save_profile` (the instruction refers to it by that name). Lets the hosted service
    swap in a Firestore-writing tool while reusing the exact same conversation logic.
    """
    return Agent(
        name="onboarding",
        model=model_factory.fast(),
        instruction=INSTRUCTION,
        tools=[save_tool],
        output_key="onboarding_result",
    )


onboarding = build_onboarding_agent(save_profile)
