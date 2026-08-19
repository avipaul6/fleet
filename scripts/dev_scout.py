#!/usr/bin/env python
"""Dev runner — see the OzBargain scout work against the LIVE feed.

    ./.venv/bin/python scripts/dev_scout.py

Shows the funnel: raw deals fetched  ->  offers the scout keeps (validated against
the Offer schema). Auto-loads .env, so you don't need to export anything.

Two halves on display:
  1. deterministic fetch/parse (no LLM, no cost) — agents/ozbargain_feed.py
  2. Gemini normalisation into Offer objects      — agents/scouts.py
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

# --- load .env into the process (Vertex project/location + isolated gcloud ADC) ---
# Done BEFORE importing Google libs so ADC resolves to the duckfleet identity.
def _load_env(path: Path) -> None:
    if not path.exists():
        print(f"!! no .env at {path} — model calls will fail. Copy .env.example and fill it.")
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

_load_env(ROOT / ".env")

# quiet the experimental/AFC noise so the output is readable
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from agents.ozbargain_feed import fetch_deals  # noqa: E402
from agents.scouts import scout_ozbargain  # noqa: E402
from schemas.offer import Offer  # noqa: E402


def _extract_json_array(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    i, j = text.find("["), text.rfind("]")
    return json.loads(text[i:j + 1]) if i != -1 and j != -1 else json.loads(text)


async def main() -> None:
    print("① Raw fetch/parse (no LLM) ......................................")
    raw = fetch_deals(limit=40)
    hinted = [d for d in raw if d["program_hint"]]
    print(f"   {len(raw)} live non-expired deals; {len(hinted)} carry a program hint.\n")

    print("② Scout agent (Gemini normalises → Offer JSON) ..................")
    runner = InMemoryRunner(agent=scout_ozbargain, app_name="dev")
    s = await runner.session_service.create_session(app_name="dev", user_id="u1")
    msg = types.Content(role="user",
                        parts=[types.Part(text="Scout OzBargain for loyalty-points offers now.")])
    final = ""
    async for ev in runner.run_async(user_id="u1", session_id=s.id, new_message=msg):
        if ev.is_final_response() and ev.content and ev.content.parts:
            final = "".join(p.text or "" for p in ev.content.parts)

    offers = _extract_json_array(final)
    print(f"   scout kept {len(offers)} of {len(raw)} deals as points-relevant offers:\n")
    ok = 0
    for obj in offers:
        try:
            o = Offer(**obj)
            ok += 1
            price = f"${o.price_aud}" if o.price_aud is not None else "$?"
            flag = f"  ⚠ tos={o.tos_risk}" if o.tos_risk != "none" else ""
            print(f"   ✓ [{o.program:16s}] {o.offer_type:14s} {price:>8s} @ {o.merchant}"
                  f"  ::  {(o.item or '')[:42]}{flag}")
        except Exception as e:
            print(f"   ✗ invalid: {str(e)[:70]}  ({obj.get('merchant')})")
    print(f"\n   {ok}/{len(offers)} validated against the Offer schema.")


if __name__ == "__main__":
    asyncio.run(main())
