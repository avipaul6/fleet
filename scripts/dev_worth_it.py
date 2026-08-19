#!/usr/bin/env python
"""Dev runner — see the worth-it gate refuse a bad errand (the governance beat).

    ./.venv/bin/python scripts/dev_worth_it.py

Two demo stops from your home (config home_lat/lng):
  A) the hero duck  — high net value, a NEAR store  -> expect DO IT
  B) a $6 collectible — low net value, a FAR store   -> expect SKIP
Drive times/distances are REAL (Google Maps Routes API via ADC). The verdict math
is deterministic Python (worth_it_verdict); the model only orchestrates + explains.
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

from agents.worth_it import worth_it, errand_cost, worth_it_verdict  # noqa: E402
from config.settings import settings  # noqa: E402

# Two candidate errands (net_value_aud would come from the valuer upstream).
STOPS = [
    {"id": "bigw-duck-2026", "merchant": "BigW Mt Gravatt", "net_value_aud": 204.40,
     "store_lat": -27.5514, "store_lng": 153.0888},
    {"id": "ooshie-far", "merchant": "Collectible @ far store", "net_value_aud": 6.00,
     "store_lat": -27.6146, "store_lng": 152.7601},
]


def _extract_json_array(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    i, j = text.find("["), text.rfind("]")
    return json.loads(text[i:j + 1]) if i != -1 and j != -1 else json.loads(text)


async def _run(agent, app: str, text: str) -> str:
    runner = InMemoryRunner(agent=agent, app_name=app)
    s = await runner.session_service.create_session(app_name=app, user_id="u1")
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    final = ""
    async for ev in runner.run_async(user_id="u1", session_id=s.id, new_message=msg):
        if ev.is_final_response() and ev.content and ev.content.parts:
            final = "".join(p.text or "" for p in ev.content.parts)
    return final


async def main() -> None:
    print(f"Home: ({settings.home_lat}, {settings.home_lng})  |  "
          f"time ${settings.time_value_aud_per_hour}/hr, fuel ${settings.fuel_aud_per_km}/km\n")

    print("① Deterministic worth-it (real Routes API drive times) ..........")
    for s in STOPS:
        trip = errand_cost(s["store_lat"], s["store_lng"])
        v = worth_it_verdict(s["net_value_aud"], trip["minutes"], trip["km"])
        mark = "✅ DO IT" if v["verdict"] == "do_it" else "⛔ SKIP"
        print(f"   {mark}  {s['merchant']}")
        print(f"        {trip['one_way_minutes']} min each way ({trip['km']} km round trip) → "
              f"trip costs ${v['trip_cost_aud']}; offer worth ${s['net_value_aud']} → "
              f"net ${v['net_after_trip_aud']}\n")

    print("② worth-it agent (orchestrates the tools + explains) ............")
    out = await _run(worth_it, "worthit", "Assess these errands:\n" + json.dumps(STOPS))
    for v in _extract_json_array(out):
        mark = "✅" if v.get("verdict") == "do_it" else "⛔"
        print(f"   {mark} {v.get('merchant')}: {v.get('verdict')} — {v.get('reason','')}")


if __name__ == "__main__":
    asyncio.run(main())
