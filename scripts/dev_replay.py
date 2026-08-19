#!/usr/bin/env python
"""Replay — render the known-good morning brief from fixtures (no live calls).

    ./.venv/bin/python scripts/dev_replay.py

Runs the deterministic core (compute_stack_value + worth_it_verdict, with drive times
frozen from real Routes measurements in fixtures/replay_offers.json) and hands the
assessed offers to the presenter agent, which composes the brief. This is the demo's
guaranteed hero output and the basis for the eval tests — same code path as live, fixed
inputs. The only model call is the presenter composing the human-facing brief.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
import warnings
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_env(path: Path) -> None:
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env(ROOT / ".env")
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from agents.valuer import compute_stack_value  # noqa: E402
from agents.worth_it import worth_it_verdict  # noqa: E402
from agents.presenter import presenter  # noqa: E402
from schemas.offer import ActionItem  # noqa: E402


def _extract_json_array(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    i, j = text.find("["), text.rfind("]")
    return json.loads(text[i:j + 1]) if i != -1 and j != -1 else json.loads(text)


def assess(offer: dict, cap: float) -> dict:
    """Deterministic: value the stack, size the buy to the cap, cost the drive."""
    price = offer["price_aud"]
    drive = offer["drive"]
    if offer.get("points_out", 0) and offer["points_out"] > 0:
        per = compute_stack_value(price, offer["points_out"], offer["program"], offer.get("multipliers"))
        units = max(1, int(cap // price))
        value = round(per["net_value_aud"] * units, 2)
        total_points = per["total_points"] * units
        cpp = per["cost_cents_per_point"]
        spend = round(price * units, 2)
    else:
        value, units, total_points, cpp, spend = offer.get("est_value_aud", 0.0), 1, 0, None, price
    v = worth_it_verdict(value, drive["minutes"], drive["km"])
    return {
        "id": offer["id"], "merchant": offer["merchant"], "item": offer.get("item"),
        "program": offer["program"], "cents_per_point": cpp, "units": units,
        "spend_aud": spend, "total_points": total_points, "offer_value_aud": value,
        "trip_minutes": drive["minutes"], "trip_km": drive["km"],
        "trip_cost_aud": v["trip_cost_aud"], "net_value_aud": v["net_after_trip_aud"],
        "verdict": v["verdict"], "requires_instore": offer.get("requires_instore", False),
        "tos_risk": offer.get("tos_risk", "none"), "weekly_cap_aud": cap,
    }


async def _present(assessed: list[dict]) -> str:
    runner = InMemoryRunner(agent=presenter, app_name="replay")
    s = await runner.session_service.create_session(app_name="replay", user_id="u1")
    msg = types.Content(role="user",
                        parts=[types.Part(text="Compose the morning brief:\n" + json.dumps(assessed))])
    final = ""
    async for ev in runner.run_async(user_id="u1", session_id=s.id, new_message=msg):
        if ev.is_final_response() and ev.content and ev.content.parts:
            final = "".join(p.text or "" for p in ev.content.parts)
    return final


ICON = {"do_it": "✅", "needs_approval": "⏳", "skip": "⛔"}


async def main() -> None:
    bundle = json.loads((ROOT / "fixtures" / "replay_offers.json").read_text())
    cap = bundle["weekly_spend_cap_aud"]
    assessed = [assess(o, cap) for o in bundle["offers"]]

    items = [ActionItem(**x) for x in _extract_json_array(await _present(assessed))]
    items.sort(key=lambda a: a.rank)
    n_do = sum(1 for a in items if a.verdict in ("do_it", "needs_approval"))
    n_skip = sum(1 for a in items if a.verdict == "skip")

    print("\n" + "=" * 68)
    print(f"🦆  DuckFleet — your hunt, {date.today():%-d %b %Y}")
    print(f"    {len(items)} candidates assessed · {n_do} to do · {n_skip} refused")
    print("=" * 68)
    for a in items:
        cpp = f" · {a.cents_per_point}c/pt" if a.cents_per_point is not None else ""
        print(f"\n {ICON.get(a.verdict,'•')}  #{a.rank}  {a.headline}")
        print(f"        net ${a.net_value_aud:,.2f}{cpp} · {a.verdict.upper()}")
        print(f"        {a.reasoning}")
        print(f"        ↳ {a.audit_ref}")
    print("\n" + "=" * 68)
    print("    Reply STOP to pause the fleet. (brief would be emailed via Gmail)")
    print("=" * 68 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
