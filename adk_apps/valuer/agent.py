"""adk web app: the valuer. Paste a JSON array of offers (each may include points_out
and a multipliers array) and it returns valued, ranked offers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _appboot  # noqa: F401  (repo root on sys.path + .env loaded)

from agents.valuer import valuer as root_agent  # noqa: E402
