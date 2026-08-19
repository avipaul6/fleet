"""adk web app: the presenter. Paste a JSON array of assessed offers and it composes
the ranked morning brief (ActionItem list)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _appboot  # noqa: F401  (repo root on sys.path + .env loaded)

from agents.presenter import presenter as root_agent  # noqa: E402
