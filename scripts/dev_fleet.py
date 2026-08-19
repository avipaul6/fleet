#!/usr/bin/env python
"""Run the WHOLE fleet through the coordinator (agents/fleet.run_fleet).

    ./.venv/bin/python scripts/dev_fleet.py           # replay (deterministic hero brief)
    ./.venv/bin/python scripts/dev_fleet.py --live     # live OzBargain scout

Renders the morning brief plus the governance summary (what got excluded, the audit
receipts). This is the end-to-end path that will deploy as the nightly job.
"""
from __future__ import annotations

import asyncio
import logging
import os
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

from agents.fleet import run_fleet  # noqa: E402

ICON = {"do_it": "✅", "needs_approval": "⏳", "skip": "⛔"}


async def main() -> None:
    replay = "--live" not in sys.argv
    mode = "replay (fixtures)" if replay else "LIVE (OzBargain feed)"
    print(f"Running the fleet — {mode} ...\n")
    result = await run_fleet(replay=replay)

    items = result["brief"]
    n_do = sum(1 for a in items if a.verdict in ("do_it", "needs_approval"))
    n_skip = sum(1 for a in items if a.verdict == "skip")

    print("=" * 70)
    print(f"🦆  DuckFleet — your hunt, {date.today():%-d %b %Y}")
    print(f"    {result['n_candidates']} candidates · {n_do} to do · {n_skip} refused "
          f"· {result['excluded_tos']} excluded (ToS)")
    print("=" * 70)
    for a in items:
        cpp = f" · {a.cents_per_point}c/pt" if a.cents_per_point is not None else ""
        print(f"\n {ICON.get(a.verdict, '•')}  #{a.rank}  {a.headline}")
        print(f"        net ${a.net_value_aud:,.2f}{cpp} · {a.verdict.upper()}")
        print(f"        {a.reasoning}")
        print(f"        ↳ {a.audit_ref}")

    print("\n" + "-" * 70)
    print("Governance receipts (audit trail):")
    for r in result["audit"]:
        extra = {k: v for k, v in r.items() if k not in ("ref", "event", "ts")}
        print(f"   • {r['event']:16} {extra if extra else ''}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
