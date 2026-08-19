"""adk web app: the OzBargain scout (fully interactive — type anything to run it)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _appboot  # noqa: F401  (repo root on sys.path + .env loaded)

from agents.scouts import scout_ozbargain as root_agent  # noqa: E402
