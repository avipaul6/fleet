"""Shared bootstrap for the adk web apps: put the repo root on sys.path and load
the root .env (Vertex project/location + isolated gcloud ADC) into the process, so
`adk web adk_apps` resolves the duckfleet identity without any manual exports.
"""
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent  # repo root
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_envf = _ROOT / ".env"
if _envf.exists():
    for _line in _envf.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())
