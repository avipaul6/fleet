# DuckFleet — The Ending (male voice-over)

Picks up right after the current last lines:
> — "Is this really deployed, or just a concept?"
> — "Anyone can try it. There's a one-click 'Open in Cloud Shell' button that deploys a
>    safe demo mode straight to Google Cloud."

Goal: add the **no-deploy** path (scan a QR → a *real* sample brief emailed to you), then
close on a memorable male-voice line. Keep the whole ending **under ~30 seconds**.

---

## A · The closing copy (this is the script)

**Male (the answerer) carries the close:**

> "And you don't even have to deploy it. Scan the code on screen, tell it what you collect
> in one sentence, and it emails you a real morning brief — the actual thing, in your inbox,
> in about a minute. No account, no card, no setup.
>
> Try the brief. If you like it, one click puts the whole fleet on your own Google Cloud.
> Either way — DuckFleet is already awake tonight, doing the hunt you'd never have time for.
> **Scan it, and see what it finds.**"

*(Optional one-line skeptic beat before the close, if you want the two-host rhythm:)*
> — "So I can see a real one before I build anything?" — "That's the whole idea."

**Silent end card (on-screen text, no voice):** keep the brand line here so you don't lose
it to the female voice —
> 🦆 **DuckFleet** — hunts hard, inside the lines. *The next duck won't get past it.*

---

## B · Get the male voice — Option 1: single-voice TTS (RECOMMENDED, reliable)

Guaranteed male voice + exact words. Reuse the Cloud Text-to-Speech you already use for the
call audio. Feed it the SSML below (a male en-AU voice keeps the Aussie tone):

```xml
<speak>
  And you don't even have to deploy it. <break time="250ms"/>
  Scan the code on screen, tell it what you collect in one sentence, and it emails you a
  real morning brief — the actual thing, in your inbox, in about a minute. <break time="300ms"/>
  No account, no card, no setup. <break time="400ms"/>
  Try the brief. If you like it, one click puts the whole fleet on your own Google Cloud. <break time="300ms"/>
  Either way — DuckFleet is already awake tonight, doing the hunt you'd never have time for. <break time="350ms"/>
  <emphasis level="moderate">Scan it, and see what it finds.</emphasis>
</speak>
```

Suggested voice: `en-AU-Neural2-B` or `en-AU-Wavenet-B` (male). Drop the resulting clip over
the held QR-code frame in InShot, then cut to the silent end card.

## B · Get the male voice — Option 2: NotebookLM (if you want the two-host style)

NotebookLM can't perfectly assign the close to the male host, but you can steer it. Make a
**separate, tiny notebook** with only the source block below, and paste the customize prompt.
Generate a few times and keep the take where the male host lands the final line; trim to it.

**Source to add (paste as the only source):**

> DuckFleet is a governed AI agent fleet on Google Cloud that hunts loyalty-points deals
> overnight and emails a ranked morning brief. There are three ways to try it, easiest first:
> (1) No deploy — scan a QR code, tell it in one sentence which programs you collect and
> where to email you, and it sends a REAL sample morning brief to your inbox in about a
> minute; no account, no card, no setup. (2) Talk to it — the same page sets up your full
> profile in natural language. (3) One click — an "Open in Cloud Shell" button deploys the
> whole fleet to your own Google Cloud project in a safe demo mode; you pay only for your own
> usage. The point of the ending is a call to action: try a real brief first, deploy only if
> you want to.

**Customize prompt:**

> This is JUST the closing 25 seconds of a two-host show — no intro, no recap, no "welcome
> back." Jump straight in on the answerer explaining that you don't have to deploy anything:
> scan a QR, get a REAL sample brief emailed to you in a minute, no account or card. One host
> is a brief skeptic ("so I can see a real one before I build anything?"); the MALE host
> answers and delivers the entire final wrap-up. Cover, fast: no-deploy sample brief → then
> one-click deploy on Google Cloud if you like it. End immediately on the male host saying:
> "Scan it, and see what it finds." No sign-off, no goodbye after that line.

---

## C · Assembly (last ~30s of the reel)

1. Hold the **QR code** full-frame (or QR + a phone mockup) while the male VO plays — long
   enough to actually scan (keep it up 6–8s).
2. Cut to the **silent brand end card** (🦆 DuckFleet tagline) for the last 2–3s.
3. Keep the QR readable at export size; test-scan the final render before you post.
