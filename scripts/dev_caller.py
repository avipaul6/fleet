#!/usr/bin/env python
"""Demo the gated stock-verification call — DuckFleet's 'meaningful action' beat.

    ./.venv/bin/python scripts/dev_caller.py

Shows the fleet (1) REFUSING to dial without approval, (2) REFUSING outside calling
hours even with approval, and (3) the approved, gated call — with REAL Cloud
Text-to-Speech audio of exactly what the AI says (it self-identifies), plus a clearly
LABELLED simulated store answer. Every path is audited.
"""
from __future__ import annotations

import logging
import os
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

from agents.verification import run_verification_call   # noqa: E402
from guardrails.gates import clear_audit, audit_trail    # noqa: E402

STORE = "BigW Mt Gravatt"
ITEM = "20 rubber ducks"
OUT = str(ROOT / "call_audio")


def main() -> None:
    clear_audit()
    print("Scenario: overnight the online stock for the duck stack reads 'unknown'.")
    print(f"The fleet wants to ring {STORE} to verify before you drive out.\n")

    print("① No approval yet — the fleet REFUSES to dial:")
    r = run_verification_call(STORE, ITEM, human_approved=False, local_hour=10)
    print(f"   → {r['status'].upper()}: {r.get('reason')}\n")

    print("② 9pm, even WITH approval — REFUSED (outside calling hours):")
    r = run_verification_call(STORE, ITEM, human_approved=True, local_hour=21)
    print(f"   → {r['status'].upper()}: {r.get('reason')}\n")

    print("③ You tap APPROVE, during hours — the gated call proceeds:")
    r = run_verification_call(STORE, ITEM, human_approved=True, local_hour=10, out_dir=OUT)
    if r["status"] == "failed":
        print(f"   → CALL FAILED: {r.get('reason')}\n")
    else:
        kind = "SIMULATED" if r["simulated"] else f"LIVE CALL → {r.get('to')} (sid {r.get('call_sid')})"
        print(f"   → {r['status'].upper()}  [{kind}]")
        print(f'     AI opens with: "{r["script"]}"')
        print(f"     Real TTS audio: {r['audio_path']}")
        print(f'     Answer: {r["answer"]}\n')

    print("Governance receipts (audit trail):")
    for a in audit_trail():
        extra = {k: v for k, v in a.items() if k not in ("ref", "event", "ts")}
        print(f"   • {a['event']:20} {extra if extra else ''}")


if __name__ == "__main__":
    main()
