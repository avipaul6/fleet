# DuckFleet — Shot List (screenshots + recordings)

Capture in order; each maps to a beat in `DEMO_SCRIPT.md`. Keep clips tight (5–15s each).
Show the **LABEL** as an on-screen caption while the hosts talk. Record at 1080p in a clean
browser profile (hide personal tabs/bookmarks); blur your real email/phone if you like.

---

## 1 · Cold open — the duck  (~15s)
- A photo of a BigW rubber duck (your own or stock). Title card: **"$3.50 → a business-class seat."**
- **Real coverage — source your own, don't fabricate:** screenshot the original OzBargain
  thread and any genuine news write-ups of the BigW-duck / Qantas-points deal (search e.g.
  *"BigW rubber duck Qantas points OzBargain"*). Verify they're real, keep each on screen
  briefly, credit the source.
- **LABEL:** *the deal only forum night-owls caught*

## 2 · Architecture  (~15s)
- Open `docs/architecture.svg` full-screen; slow pan/zoom left→right along the flow.
- **LABEL:** *governed agent fleet · Google Cloud*

## 3 · Onboarding — natural language  (~25s) · SCREEN RECORDING
- Run `./.venv/bin/adk web adk_apps`, open the app dropdown → **onboarding**.
- Type: *"I collect Qantas and Flybuys, no more credit cards, I'd switch electricity or NBN
  for good points, $100 a week, brief to me@example.com"* → send.
- Show the `save_profile` tool-call events and the confirmation reply.
- **LABEL:** *set up by conversation → writes profile.json*

## 4 · The morning brief  (~25s) · SCREEN RECORDING / screenshot
- Best: the real email in Gmail (proves delivery). To guarantee the rich hero brief:
  ```bash
  DUCKFLEET_REPLAY=true ./.venv/bin/python -m runtimes.gcp_adk.job
  ```
  then open the email it sends. (Or the local HTML preview.)
- Scroll slowly: the **points-first TOP PICK**, the **SKIPPED** list with honest reasons,
  the **Activate / Add-reminder** buttons.
- **LABEL:** *points-first · honest skips · one-click actions*

## 5 · Governance + ROI  (~20s)
- In the same brief, hold on the SKIPPED reasons and the **🧮 Run economics** line.
- Optional BigQuery proof (terminal or console):
  ```bash
  bq query --use_legacy_sql=false \
    "SELECT mode, COUNT(*) AS n, ROUND(AVG(net_value_aud),2) AS avg_net FROM duckfleet.offer_history GROUP BY mode"
  ```
- **LABEL:** *refuses · respects you · knows its own ROI*

## 6 · The gated call — hero beat  (~30s) · SCREEN RECORDING + audio + phone
- Run `./.venv/bin/python scripts/dev_caller.py` — show it **REFUSE** (no approval),
  **REFUSE** (after-hours), then the approved **CALL**.
- Record your **phone actually ringing** and the audio (*"Hi, I'm an AI assistant…"*). You
  already have the real Twilio call and the TTS file in `call_audio/`.
- **LABEL:** *real action — gated, self-identifying, logged*

## 7 · Proof on Google Cloud + one-click  (~20s) · SCREEN RECORDING
- Console → **Cloud Run → Jobs → duckfleet-nightly**: show a green execution, open **Logs**
  (the `fleet_run_complete` / `brief_emailed` line). **This is the required GCP proof.**
- Then the README **"Open in Cloud Shell"** button → Cloud Shell opening with the tutorial.
- **LABEL:** *deployed: Cloud Run Job on Vertex AI · one-click to try*

## 8 · Close  (~10s)
- Title card: 🦆 **DuckFleet — governed agency on Google Cloud.**
  *"Hunts hard, inside the lines. The next duck won't get past it."*

---

### Assemble
Lay these over the NotebookLM audio along the `DEMO_SCRIPT.md` beats. Target **2:30–3:00**;
trim ruthlessly — shorter and punchy wins. Keep the **call audio** un-cut; it's the moment.
