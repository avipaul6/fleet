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

from agents.fleet import run_fleet          # noqa: E402
from agents.delivery import render_text      # noqa: E402


async def main() -> None:
    replay = "--live" not in sys.argv
    mode = "replay (fixtures)" if replay else "LIVE (OzBargain feed)"
    print(f"Running the fleet — {mode} ...\n")
    result = await run_fleet(replay=replay)

    # exactly what the email will contain
    print(render_text(result))

    print("\n" + "-" * 32)
    print("Governance receipts (audit trail):")
    for r in result["audit"]:
        extra = {k: v for k, v in r.items() if k not in ("ref", "event", "ts")}
        print(f"   • {r['event']:16} {extra if extra else ''}")


if __name__ == "__main__":
    asyncio.run(main())
