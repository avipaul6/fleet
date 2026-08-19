"""Cloud Run Job entrypoint — the nightly fleet run.

Runtime ADAPTER only: it wires run_fleet() to the platform (env, structured logging,
exit code). No fleet/guardrail/schema logic lives here — that stays in agents/.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

# Dev convenience: load .env when running locally. In Cloud Run the config arrives as
# real env vars (--set-env-vars) and there is no .env, so this is a no-op there.
_envf = _ROOT / ".env"
if _envf.exists():
    for _l in _envf.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

from agents.fleet import run_fleet                                      # noqa: E402
from agents.delivery import gmail_configured, send_brief, render_text    # noqa: E402
from config.settings import settings                                    # noqa: E402


async def _main() -> None:
    replay = os.environ.get("DUCKFLEET_REPLAY", "false").lower() in ("1", "true", "yes")
    result = await run_fleet(replay=replay)
    brief = [a.model_dump() for a in result["brief"]]

    # Cloud Logging captures stdout — one structured line summarising the run.
    print(json.dumps({
        "event": "fleet_run_complete",
        "mode": "replay" if replay else "live",
        "n_candidates": result["n_candidates"],
        "excluded_tos": result["excluded_tos"],
        "brief": brief,
    }, default=str))

    # Deliver via Gmail if configured; otherwise say exactly what's missing (never silent).
    if gmail_configured():
        subject = f"🦆 DuckFleet — Daily Hunt, {date.today():%-d %b %Y}"
        send_brief(subject, render_text(result))
        print(json.dumps({"event": "brief_emailed", "to": settings.notify_email}))
    else:
        missing = [name for name, val in [
            ("DUCKFLEET_NOTIFY_EMAIL", settings.notify_email),
            ("DUCKFLEET_GMAIL_CLIENT_ID", settings.gmail_client_id),
            ("DUCKFLEET_GMAIL_CLIENT_SECRET", settings.gmail_client_secret),
            ("DUCKFLEET_GMAIL_REFRESH_TOKEN", settings.gmail_refresh_token),
        ] if not val]
        print(json.dumps({"event": "brief_not_emailed", "missing_config": missing}))


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
