"""adk web app: the worth-it gate. Paste a JSON array of errands (each with
net_value_aud, store_lat, store_lng) and it computes real drive economics + a verdict."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _appboot  # noqa: F401  (repo root on sys.path + .env loaded)

from agents.worth_it import worth_it as root_agent  # noqa: E402
