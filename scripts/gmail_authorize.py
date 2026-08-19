#!/usr/bin/env python
"""One-time: authorize DuckFleet to send email as your Gmail (gmail.send scope only).

Prereq: in the GCP console (APIs & Services -> Credentials) create an OAuth client of
type **Desktop app**, then put its id/secret in .env:
    DUCKFLEET_GMAIL_CLIENT_ID=...
    DUCKFLEET_GMAIL_CLIENT_SECRET=...

Then run this once and consent in the browser AS THE SENDER account (duckfleet.dev):
    ./.venv/bin/python scripts/gmail_authorize.py

It prints a refresh token. Paste it into .env as DUCKFLEET_GMAIL_REFRESH_TOKEN (or push
to Secret Manager). That token is the only secret the app needs to send — no password,
no re-consent.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_envf = ROOT / ".env"
if _envf.exists():
    for _l in _envf.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main() -> int:
    cid = os.environ.get("DUCKFLEET_GMAIL_CLIENT_ID", "").strip()
    csec = os.environ.get("DUCKFLEET_GMAIL_CLIENT_SECRET", "").strip()
    if not (cid and csec):
        print("Set DUCKFLEET_GMAIL_CLIENT_ID and DUCKFLEET_GMAIL_CLIENT_SECRET in .env first "
              "(create a Desktop OAuth client in the GCP console).")
        return 1

    from google_auth_oauthlib.flow import InstalledAppFlow

    client_config = {"installed": {
        "client_id": cid,
        "client_secret": csec,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }}
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    if not creds.refresh_token:
        print("No refresh token returned. Revoke prior access and retry with prompt=consent.")
        return 1
    print("\n✅ Authorized. Add this to your .env (keep it secret — never commit):\n")
    print(f"DUCKFLEET_GMAIL_REFRESH_TOKEN={creds.refresh_token}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
