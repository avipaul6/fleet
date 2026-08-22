# DuckFleet — Shot List (screenshots + recordings)

Capture in order; each maps to a beat in `DEMO_SCRIPT.md`. Keep clips tight (5–15s each).
Show the **LABEL** as an on-screen caption while the hosts talk. Record at 1080p in a clean
browser profile (hide personal tabs/bookmarks); blur your real email/phone if you like.

> **Running-order principle (why this order):** the email brief *looks like a newsletter*, so
> we never lead with it. We lead with the things a newsletter can **never** do — refuse, act,
> and self-govern — and show the brief last, reframed as *the receipt*, not the product.
> The through-line caption voice is **verbs of agency**: *decides · refuses · calls · self-governs · logs*.

---

## 1 · Cold open — the duck  (~15s)
- A photo of a BigW rubber duck (your own or stock). Title card: **"$3.50 → a business-class seat."**
- **Real coverage — source your own, don't fabricate:** screenshot the original OzBargain
  thread and any genuine news write-ups of the BigW-duck / Qantas-points deal (search e.g.
  *"BigW rubber duck Qantas points OzBargain"*). Verify they're real, keep each on screen
  briefly, credit the source.
- **LABEL:** *the deal only forum night-owls caught*

## 2 · Brand reveal — the fleet  (~6s)
- The Veo fleet plate (ducks → moonlit horizon), wordmark drops in: 🦆 **DuckFleet**,
  tagline under it: *"An agent fleet that hunts loyalty points while you sleep."*
- **LABEL:** *(none — let the wordmark + tagline breathe)*

## 3 · Kill the objection  (~4s) · TITLE CARD
- Hard, plain title card over black or the fleet plate:
  **"This isn't a newsletter. It decides, it refuses, and it acts."**
- Say the objection out loud, then spend the rest of the video proving it. Everything after
  this card is evidence for this one sentence.
- **LABEL:** *(the card is the label)*

## 4 · Architecture  (~12s)
- Open `docs/architecture.svg` full-screen; slow pan/zoom left→right along the flow.
- Land the pan on the **guardrail gates** and the **caller** node — foreshadow the agency.
- **LABEL:** *governed agent fleet · Google Cloud*

## 5 · Onboarding — natural language  (~20s) · SCREEN RECORDING
- Run `./.venv/bin/adk web adk_apps`, open the app dropdown → **onboarding**.
- Type: *"I collect Qantas and Flybuys, no more credit cards, I'd switch electricity or NBN
  for good points, $100 a week, brief to me@example.com"* → send.
- Show the `save_profile` tool-call events and the confirmation reply.
- **LABEL:** *set up by conversation → writes profile.json*

## 6 · THE HERO BEAT — it refuses, then it acts  (~35s) · SCREEN RECORDING + audio + phone/video
- **This is the first product payoff. Nothing a newsletter does looks like this.**
- Run `./.venv/bin/python scripts/dev_caller.py`. Show, in order:
  1. **REFUSE** — no human approval yet. Hold on the gate log line.
  2. **REFUSE** — after-hours / call-window closed. Hold on the reason.
  3. **APPROVED → CALL** — the gate opens and the fleet dials.
- Cut to the **store-call simulation** (see `CALL_SIM.md`): phone rings, a shop worker answers,
  and your **real Twilio/TTS audio** plays over it — *"Hi, I'm an AI assistant calling on behalf
  of a customer…"* — worker replies *"No, we're out of stock."* Keep this audio **un-cut**; it's the moment.
- Land the result back in the fleet: stock **not confirmed → errand dropped**, logged.
- **LABEL:** *real action — gated · self-identifying · logged · takes "no" for an answer*

## 7 · Governance + ROI  (~18s) · SCREEN RECORDING
- Show the deterministic **worth-it** math rejecting a drive (*not worth the fuel/time*) —
  the LLM finds stacks, **Python does the arithmetic**.
- Hold on the **🧮 Run economics** / ROI line: it knows whether the run paid for itself.
- Optional BigQuery proof (terminal or console):
  ```bash
  bq query --use_legacy_sql=false \
    "SELECT mode, COUNT(*) AS n, ROUND(AVG(net_value_aud),2) AS avg_net FROM duckfleet.offer_history GROUP BY mode"
  ```
- **LABEL:** *does the math · refuses the bad ones · knows its own ROI*

## 8 · The brief — the receipt (NOT the product)  (~18s) · SCREEN RECORDING / screenshot
- Best: the real email in Gmail (proves delivery). To guarantee the rich hero brief:
  ```bash
  DUCKFLEET_REPLAY=true ./.venv/bin/python -m runtimes.gcp_adk.job
  ```
  then open the email it sends. (Or the local HTML preview.)
- **Do NOT scroll the deals like a newsletter.** Hold on what a newsletter doesn't have:
  the **SKIPPED list with honest reasons** and the **run-ROI line**. The brief is the record
  of decisions it made and refused — the receipt, not a content feed.
- Then the **Activate / Add-reminder** one-click buttons: the human stays in the loop.
- **LABEL:** *the receipt — every decision it made, and the ones it refused*

## 9 · Proof on Google Cloud + one-click  (~18s) · SCREEN RECORDING
- Console → **Cloud Run → Jobs → duckfleet-nightly**: show a green execution, open **Logs**
  (the `fleet_run_complete` / `brief_emailed` line). **This is the required GCP proof.**
- Then the README **"Open in Cloud Shell"** button → Cloud Shell opening with the tutorial.
- **LABEL:** *deployed: Cloud Run Job on Vertex AI · one-click to try*

## 10 · Close  (~10s)
- Title card: 🦆 **DuckFleet — governed agency on Google Cloud.**
  *"Hunts hard, inside the lines. The next duck won't get past it."*

---

### Assemble
Lay these over the NotebookLM audio along the `DEMO_SCRIPT.md` beats. Target **2:30–3:00**;
trim ruthlessly — shorter and punchy wins. Keep the **call audio** un-cut; it's the moment.

**Order matters:** lead with agency (refuse + act), show the brief as a *receipt* near the end.
If a viewer's first concrete impression is the email, they file it as a newsletter and you
spend the rest of the video fighting that. Beat 6 is what makes it un-newsletter-able — protect
its runtime.
