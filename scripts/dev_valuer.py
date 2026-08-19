#!/usr/bin/env python
"""Dev runner — see the valuer turn offers into points value.

    ./.venv/bin/python scripts/dev_valuer.py

Two parts:
  1. The deterministic hero-stack proof (no LLM) — the $3.50 duck math, guaranteed.
  2. The live pipeline slice: OzBargain scout -> valuer, with the hero duck injected so
     there's always a hero to rank. The valuer calls compute_stack_value (python does
     the arithmetic; the model only routes numbers and ranks).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_env(path: Path) -> None:
    if not path.exists():
        print(f"!! no .env at {path} — model calls will fail.")
        return
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

from agents.scouts import scout_ozbargain  # noqa: E402
from agents.valuer import valuer, compute_stack_value  # noqa: E402


def _extract_json_array(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    i, j = text.find("["), text.rfind("]")
    return json.loads(text[i:j + 1]) if i != -1 and j != -1 else json.loads(text)


def _hero_offer() -> dict:
    data = json.loads((ROOT / "fixtures" / "hero_duck.json").read_text())
    o = dict(data["offer"])
    o["multipliers"] = data["multipliers"]
    o["item"] = "rubber duck (hero fixture)"
    return o


async def _run(agent, app: str, text: str) -> str:
    runner = InMemoryRunner(agent=agent, app_name=app)
    s = await runner.session_service.create_session(app_name=app, user_id="u1")
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    final = ""
    async for ev in runner.run_async(user_id="u1", session_id=s.id, new_message=msg):
        if ev.is_final_response() and ev.content and ev.content.parts:
            final = "".join(p.text or "" for p in ev.content.parts)
    return final


def _money(v):
    return f"${v:,.2f}" if isinstance(v, (int, float)) else "—"


async def main() -> None:
    hero = _hero_offer()

    print("① Hero-stack proof — the $3.50 duck (deterministic, no LLM) ......")
    r = compute_stack_value(hero["price_aud"], hero["points_out"], hero["program"], hero["multipliers"])
    print(f"   1 duck : {r['total_points']:,} pts @ {r['cost_cents_per_point']}c/pt"
          f"  →  net {_money(r['net_value_aud'])}  ({r['value_multiple']}x value)")
    cap, price = 100.0, hero["price_aud"]
    n = int(cap // price)
    print(f"   {n} ducks: {r['total_points'] * n:,} pts, {_money(price * n)} spend (under "
          f"{_money(cap)} cap)  →  net {_money(r['net_value_aud'] * n)}\n")

    print("② Live pipeline: OzBargain scout → valuer .......................")
    scout_out = await _run(scout_ozbargain, "scout", "Scout OzBargain for loyalty-points offers now.")
    try:
        offers = _extract_json_array(scout_out)
    except Exception:
        offers = []
    offers.append(hero)  # always give the valuer a hero to rank
    print(f"   valuing {len(offers)} offers ({len(offers) - 1} scouted + 1 hero duck)...\n")

    valued_out = await _run(valuer, "valuer", "Value these offers:\n" + json.dumps(offers))
    valued = _extract_json_array(valued_out)
    valued.sort(key=lambda v: (v.get("net_value_aud") is not None, v.get("net_value_aud") or 0), reverse=True)

    print(f"   {'#':<2} {'program':16} {'c/pt':>6} {'net':>10}  merchant / note")
    print("   " + "-" * 74)
    for i, v in enumerate(valued, 1):
        cpp = v.get("cost_cents_per_point")
        cpp_s = f"{cpp}" if cpp is not None else "—"
        note = v.get("note") or ("no points angle" if v.get("net_value_aud") is None else "")
        print(f"   {i:<2} {str(v.get('program','?')):16} {cpp_s:>6} {_money(v.get('net_value_aud')):>10}"
              f"  {v.get('merchant','?')}  ::  {note[:38]}")


if __name__ == "__main__":
    asyncio.run(main())
