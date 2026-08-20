"""adk web app: the onboarding assistant — chat to build your profile (writes profile.json)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _appboot  # noqa: F401  (repo root on sys.path + .env loaded)

from agents.onboarding import onboarding as root_agent  # noqa: E402
