"""Central config. Everything overridable via env — including models per tier."""
import json
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- GCP ---
    project_id: str = "your-gcp-project"
    region: str = "us-central1"
    # Set (e.g. "duckfleet") to append each run's offers to BigQuery offer_history.
    # Empty = disabled (best-effort sink; never blocks the brief).
    bigquery_dataset: str = ""

    # --- Model tiers (THE SWITCH) ---
    # Plain string -> native Gemini via ADK.
    # "vertex_ai/..." or "litellm/..." prefix -> LiteLlm wrapper (e.g. Claude on
    # Vertex AI Model Garden). Still 100% inside GCP.
    model_fast: str = "gemini-3.5-flash"      # scouts, worth-it, presenter
    # Hackathon REQUIRES Gemini 3+. 3.x Pro wasn't available to the project (404), so both
    # tiers default to the GA 3.5-flash; swap STRONG to a 3.x Pro via env once granted.
    model_strong: str = "gemini-3.5-flash"    # coordinator, valuer, caller

    # --- Household profile (hackathon: hardcode, don't build OAuth) ---
    home_lat: float = -27.5236   # Tarragindi-ish; set yours
    home_lng: float = 153.0413
    programs: list[str] = ["qantas_ff", "flybuys", "everyday_rewards"]
    cards: list[str] = ["qantas_amex"]
    time_value_aud_per_hour: float = 60.0
    fuel_aud_per_km: float = 0.16
    # Category preferences: avoid = always skip (shown in brief, with reason);
    # conditional = surface only if net value clears the $ bar; else "want" (default).
    prefs_avoid: list[str] = ["credit_card"]
    prefs_conditional: dict[str, float] = {"insurance": 300.0}
    # Where the morning brief is emailed (hackathon: one recipient in config;
    # later: per-user from the profile UI). Set DUCKFLEET_NOTIFY_EMAIL in .env.
    notify_email: str = ""

    # Gmail send credentials — read ONLY from env / Secret Manager, NEVER hardcoded
    # or committed. Get a refresh token once via scripts/gmail_authorize.py.
    gmail_sender: str = ""          # e.g. duckfleet.dev@gmail.com (blank -> "me")
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_refresh_token: str = ""

    # Phone verification (Twilio) — creds ONLY from env/Secret Manager, never committed.
    # verify_phone_number = who to call (test: YOUR OWN number; prod: the store's).
    # Blank/unset = fall back to the labelled call simulation.
    verify_phone_number: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    # Trial accounts can't pass inline TwiML — point this at a TwiML Bin URL (or the
    # Twilio demo doc) and we call with `url=` instead. Blank = inline TwiML (paid accounts).
    twilio_twiml_url: str = ""

    # --- Guardrails (hard limits, not suggestions) ---
    spend_cap_aud_per_week: float = 100.0
    max_calls_per_store_per_day: int = 1
    call_window_local: tuple[int, int] = (9, 17)   # only call 9am-5pm
    require_human_approval_for: list[str] = ["phone_call", "purchase"]

    model_config = {"env_prefix": "DUCKFLEET_"}


settings = Settings()

# Apply the onboarding profile (profile.json) on top of env/defaults, if present.
# This is exactly what the onboarding agent writes — the fleet reads it here.
_profile_path = Path(__file__).resolve().parent.parent / "profile.json"
if _profile_path.exists():
    try:
        for _k, _v in json.loads(_profile_path.read_text()).items():
            if hasattr(settings, _k) and _v not in (None, [], {}):
                setattr(settings, _k, _v)
    except Exception:
        pass
