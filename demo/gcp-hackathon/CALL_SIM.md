# CALL_SIM — the gated store call (Shot 6 hero beat)

The **call is real** (real Twilio call + real Cloud TTS audio in `call_audio/`). The **shop
worker on screen is a re-enactment.** Label it. Honesty > fakery — it's the whole differentiator.

On-screen tag for the worker footage: **"Simulated — dramatisation of a real automated call."**
(Small, bottom corner. Your genuine TTS audio needs no such tag; it's the real thing.)

---

## What the viewer should experience (10–12s)

1. DuckFleet dials (from the `dev_caller.py` screen recording — the APPROVED → CALL step).
2. A discount-store counter. A phone rings. A worker answers.
3. Over it, your **real AI TTS** plays:
   > "Hi, I'm an AI assistant calling on behalf of a customer. Just a quick question if you have
   > a moment. Do you currently have 20 rubber ducks in stock?"
4. The worker checks, shrugs, replies: **"No, sorry — we're out of stock."**
5. Cut back to the fleet: **stock not confirmed → errand dropped → logged.**

---

## Build it in LAYERS (do NOT rely on Veo's audio)

Generate the **visual silent**, and control **all audio in InShot**. This keeps your real TTS
pristine and avoids Veo garbling the dialogue. Four audio layers, stacked:

| Layer | Source | Timing |
|---|---|---|
| Phone ring SFX | free SFX (e.g. a 2-ring landline) | 0.0–2.0s, before pickup |
| **AI caller line** | your real `call_audio/` TTS (the 3 sentences above) | starts as worker lifts handset (~2.0s) |
| Worker reply | short clean VO — generate a TTS line or record a mate | after the AI line ends |
| Room tone / counter ambience | quiet retail hum, low | under everything |

**Worker reply line to generate/record** (keep it short so loose lip-sync still reads):
> "No, sorry — we're all out of stock right now."

Lip-sync tip: you will *not* get perfect sync from Veo. Two ways to dodge it:
- Frame the reply so the worker is **turning away / looking at a shelf or screen** as they say it
  (mouth not in tight focus), or
- Cut to the **DuckFleet screen** ("stock not confirmed") *over* the worker's reply audio, so the
  line lands on the UI, not the face. This is cleaner and reinforces the product.

---

## Veo prompt — the store answers (silent visual)

> Cinematic, 8 seconds, single take, realistic documentary style. Inside a busy Australian
> discount department store: a friendly retail worker in a plain apron stands behind a service
> counter under bright fluorescent light, shelves of colourful boxed toys blurred behind them.
> **Seconds 0–2:** a counter phone rings; the worker glances over and reaches for the handset.
> **Seconds 2–5:** the worker lifts the phone to their ear and listens, a polite, slightly
> everyday expression, nodding once. **Seconds 5–8:** the worker glances toward the shelves,
> gives a small apologetic shrug and shake of the head, and speaks briefly. Natural handheld
> motion, warm realistic lighting, shallow depth of field. No on-screen text, no brand logos,
> no readable signage.

Notes:
- "**glances toward the shelves… shake of the head**" gives you the *visual* of "out of stock"
  even with the audio muted, and the turn-of-head is your lip-sync cover.
- Keep it a **generic** worker/apron — no Big W branding (Veo garbles logos; you don't want a
  fake real-brand employee anyway). Add "BigW · Australia" as a text overlay later if you must,
  same as the cold open.

### Alternate framings (pick by what cuts best)
- **Over-the-shoulder / phone on counter:** worker's back to us, picks up a handset on the
  counter — removes the lip-sync problem entirely; you hear the call, see the listener.
- **Split screen:** left = DuckFleet dialing UI, right = worker answering. Literally shows
  "software → real world" in one frame. Strong for the "it acts" point.

---

## Assembly order for Shot 6 (matches SHOT_LIST.md)

1. `dev_caller.py` screen rec: **REFUSE** (no approval) → **REFUSE** (after-hours) → **APPROVED → CALL**.
2. Store-answers video (this file) + layered audio (real TTS + ring + reply + ambience).
3. Cut to fleet result: **not confirmed → errand dropped → logged.**

Keep the **real TTS audio un-cut**. The refusals *before* the call are what make the call land —
a newsletter never has to ask permission, and never takes "no" for an answer. That's the beat.
