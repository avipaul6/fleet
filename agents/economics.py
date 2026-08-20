"""Run economics — DuckFleet governing its OWN worth.

The fleet asks "is this errand worth your time and fuel?" — this applies the same
question to the agent itself: did this run's compute cost (LLM tokens + API calls)
earn its keep against the value it surfaced? Powers a ROI line in the brief and a
"quiet night" signal so the fleet never burns credit for nothing.

Prices are ORDER-OF-MAGNITUDE estimates in AUD — tune to your billing; the point is
the ratio, not penny precision.
"""
from __future__ import annotations

# Approximate AUD unit prices (estimates).
_GEMINI_IN_PER_TOKEN = 0.20 / 1_000_000     # fast-tier input
_GEMINI_OUT_PER_TOKEN = 0.80 / 1_000_000    # fast-tier output
_ROUTES_PER_CALL = 0.005                    # Maps Routes
_TTS_PER_CHAR = 4.0 / 1_000_000             # Text-to-Speech
_TWILIO_PER_CALL = 0.02                     # outbound call (approx)


class RunCost:
    """Accumulates a single run's compute cost."""

    def __init__(self) -> None:
        self.in_tokens = 0
        self.out_tokens = 0
        self.llm_calls = 0
        self.routes_calls = 0
        self.tts_chars = 0
        self.twilio_calls = 0

    def add_llm(self, in_tokens: int, out_tokens: int) -> None:
        self.in_tokens += int(in_tokens or 0)
        self.out_tokens += int(out_tokens or 0)
        self.llm_calls += 1

    def add_routes(self, n: int = 1) -> None:
        self.routes_calls += n

    def add_tts(self, chars: int) -> None:
        self.tts_chars += int(chars or 0)

    def add_twilio(self, n: int = 1) -> None:
        self.twilio_calls += n

    @property
    def total_aud(self) -> float:
        return round(
            self.in_tokens * _GEMINI_IN_PER_TOKEN
            + self.out_tokens * _GEMINI_OUT_PER_TOKEN
            + self.routes_calls * _ROUTES_PER_CALL
            + self.tts_chars * _TTS_PER_CHAR
            + self.twilio_calls * _TWILIO_PER_CALL,
            4,
        )

    def breakdown(self) -> dict:
        return {
            "aud": self.total_aud,
            "llm_calls": self.llm_calls,
            "tokens_in": self.in_tokens, "tokens_out": self.out_tokens,
            "routes_calls": self.routes_calls,
        }


def worth_running(value_aud: float, cost_aud: float) -> dict:
    """Compare value surfaced against compute spent. ROI = value / cost."""
    value_aud = round(value_aud or 0.0, 2)
    roi = round(value_aud / cost_aud, 1) if cost_aud > 0 else None
    if value_aud <= 0:
        verdict = "quiet_night"      # cheap run, nothing cleared the bar
    elif roi is not None and roi < 1:
        verdict = "not_worth_it"     # spent more compute than value found
    else:
        verdict = "worth_it"
    return {"value_aud": value_aud, "cost_aud": cost_aud, "roi": roi, "verdict": verdict}
