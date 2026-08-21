# DuckFleet — Demo Video Script

**Format:** podcast-style — two hosts in conversation (audio) laid over real-app visuals
(screen recordings + screenshots). Not talking heads.
**Length:** aim **~2:30–3:00**. Shorter and punchy beats a padded 4 minutes.
**Must include (hackathon rules):** the app working in real time **and** proof of the Google
Cloud backend (show the Cloud Run Job + logs).

**Companion files (same folder):**
- **`PODCAST_SOURCE.md`** — feed this to **NotebookLM** to *generate* the two-host audio.
- **`SHOT_LIST.md`** — exactly what to screen-record / screenshot, in order.

Workflow: generate the audio from `PODCAST_SOURCE.md` → capture the clips in `SHOT_LIST.md`
→ lay the visuals over the audio along the beats below → trim.

---

## The beats (audio intent → visual)

### 1 · Cold open — the duck  (~0:00–0:18)
- **Hosts:** *"Remember the $3.50 BigW rubber duck that was secretly a business-class
  ticket?" — "The one where stacking promos earned Qantas points at half a cent each, and
  only the OzBargain night-owls caught it?"*
- **Visual:** duck photo + real OzBargain/news screenshots · title card *"$3.50 → a
  business-class seat"* (SHOT_LIST #1).

### 2 · The idea, on Google Cloud  (~0:18–0:45)
- **Hosts:** *"So I built a fleet of agents to hunt the next duck while I sleep." — "On
  Google Cloud?" — "All of it. Every night it scouts, does the maths, and emails me a
  ranked list — only what's worth my time. It refuses the rest."*
- **Visual:** architecture diagram, slow pan (SHOT_LIST #2).

### 3 · Onboarding — you just tell it  (~0:45–1:12)
- **Hosts:** *"But everyone wants different things." — "You just tell it. Watch —" (reads
  the typed line) — "And it understood all that?"*
- **Visual:** onboarding chat recording → `save_profile` → confirmation (SHOT_LIST #3).

### 4 · The morning brief — the payoff  (~1:12–1:40)
- **Hosts:** *"Next morning, this lands in my inbox." — "Top one's a real win?" — "Sixteen
  thousand Qantas points. And it skipped the credit cards because I asked — and tells me
  why it skipped the rest. No fake 'no points' excuses."*
- **Visual:** the email — scroll the points-first top pick + honest skips (SHOT_LIST #4).

### 5 · Governance — refusal + ROI  (~1:40–2:05)
- **Hosts:** *"It refuses things?" — "That's the whole point. It won't drive 40 minutes for
  a $6 toy, won't touch a ToS loophole — and it even knows when *it* isn't worth running.
  Look, it reports its own ROI."*
- **Visual:** SKIPPED reasons + the 🧮 run-economics line; quick BigQuery shot (SHOT_LIST #5).

### 6 · THE gated call — hero beat  (~2:05–2:35)
- **Hosts:** *"But does it actually DO anything?" — "It can — gated. Stock's unknown, it
  wants to call the store. I tap approve…" (phone rings; play the audio) — AI voice: "Hi,
  I'm an AI assistant calling on behalf of a customer…" — "It said it's an AI!" — "Every
  action asks first, and it's all logged."*
- **Visual:** caller demo (refuse → approve) + real phone ringing + the call audio (SHOT_LIST #6).

### 7 · Proof + one-click try  (~2:35–2:58)
- **Hosts:** *"And it's really deployed?" — "Nightly Cloud Run Job on Vertex AI — here's a
  green run and the logs. And anyone can deploy their own with one click."*
- **Visual:** Cloud Console (Job + green execution + logs), then the Cloud Shell button
  (SHOT_LIST #7). **This is the required GCP proof.**

### 8 · Close  (~2:58–3:08)
- **Hosts:** *"So — an agent you can trust with real actions." — "Hunts hard, inside the
  lines. The next duck won't get past it."*
- **Visual:** close on the brief / duck card + tagline (SHOT_LIST #8).

---

## Notes
- The **call audio is the star** — actually play it.
- **Caption every visual** (labels in SHOT_LIST) so the conversation stays anchored.
- If NotebookLM's audio runs long, trim to these beats or tighten the customize prompt.
- **Bonus points:** the NotebookLM podcast doubles as a "published podcast"; post with
  **#AllThingsAgentic**.
