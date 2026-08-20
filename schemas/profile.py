"""The household profile the onboarding agent writes and the fleet reads.

This is the contract between the interactive onboarding surface (a chat agent) and the
headless fleet. Written to profile.json locally; a Firestore doc in a multi-user future.
"""
from pydantic import BaseModel
from typing import Literal

Program = Literal["qantas_ff", "velocity", "flybuys", "everyday_rewards"]
Category = Literal["credit_card", "insurance", "energy", "telco", "groceries",
                   "subscription", "collectible", "shopping", "other"]


class Profile(BaseModel):
    programs: list[Program] = []
    prefs_avoid: list[Category] = []                # never surface these
    prefs_conditional: dict[str, float] = {}        # category -> min net $ to surface
    spend_cap_aud_per_week: float | None = None
    time_value_aud_per_hour: float | None = None
    notify_email: str | None = None
    home_label: str | None = None                   # suburb/postcode (geocoded later)

    def to_settings_overrides(self) -> dict:
        """Only the keys that map onto Settings fields (home_label is informational)."""
        out = {"programs": self.programs, "prefs_avoid": self.prefs_avoid,
               "prefs_conditional": self.prefs_conditional}
        if self.spend_cap_aud_per_week is not None:
            out["spend_cap_aud_per_week"] = self.spend_cap_aud_per_week
        if self.time_value_aud_per_hour is not None:
            out["time_value_aud_per_hour"] = self.time_value_aud_per_hour
        if self.notify_email:
            out["notify_email"] = self.notify_email
        return out
