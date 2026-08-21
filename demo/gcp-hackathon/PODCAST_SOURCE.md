# DuckFleet — Podcast Source (for NotebookLM Audio Overview)

**How to use:** create a NotebookLM notebook, add this file as a source, open
**Audio Overview → Customize**, paste the prompt at the very bottom, and generate. It
produces the two-host conversation for the demo — and doubles as a standalone published
podcast (a scored bonus). Trim/re-generate if it runs long.

---

## The story

It started with a rubber duck. In 2025 a $3.50 bath toy at BigW became briefly famous in
Australian bargain circles: bought in bulk and stacked across promotions — a store bonus, a
shopping-portal multiplier, a credit-card offer — it earned Qantas Points at about half a
cent each. Do the maths and that pile of $3.50 ducks was, effectively, a business-class
seat. The only people who caught it were forum obsessives refreshing OzBargain at midnight.

That's the itch DuckFleet scratches: the value is real, but catching it is a full-time,
tedious hunt. The idea — hunt the next duck automatically, while you sleep.

## What DuckFleet is

DuckFleet is a background fleet of AI agents on Google Cloud. Every night a Cloud Run Job
wakes up and a team of agents does the heavy lifting: scouts read the deal feeds, a valuer
does the stacking maths (cents-per-point), a worth-it agent weighs drive time and petrol
against the reward, and a presenter emails you a ranked morning brief. You wake up to a
short list of what's actually worth doing — and, just as importantly, what to skip.

## The twist — it's governed

Most "agents" just do stuff. DuckFleet's whole personality is restraint. It refuses errands
that aren't worth the drive — 40 minutes for a $6 toy? Skip, and it says why. It respects
your preferences: tell it "no more credit cards" and it ignores cards worth thousands of
nominal points, and tells you it did. It won't touch a deal that breaks a loyalty program's
terms. Every real-world action is gated behind your explicit approval, with a logged audit
trail.

It's honest about the boring stuff too. Instead of inventing "no points" excuses it gives
the real reason — "Velocity isn't a program you collect", or "only worth it if you'd already
spend $50 at Coles anyway."

## You set it up just by talking to it

There's no settings form. You tell an onboarding agent, in plain language: "I collect Qantas
and Flybuys, no more credit cards, I'd switch electricity or NBN for good points, a hundred
dollars a week." It understands that and writes your profile — and the nightly fleet reads
it. Natural language in, working config out.

## It can actually act — carefully

Here's the part people don't expect: it can pick up the phone. If a deal depends on stock
and the store's availability is unknown, DuckFleet can call the store to check — but only
after it asks you, only within calling hours, only once per store, and it opens the call by
identifying itself as an AI. You hear a real phone ring and a real voice say, "Hi, I'm an AI
assistant calling on behalf of a customer." A genuine action taken on your behalf, inside
strict guardrails.

## It even governs its own cost

DuckFleet applies its own "is this worth it?" test to itself. Each run it tallies what it
spent in compute — model tokens, API calls — against the value it surfaced, and reports the
ROI. On a quiet night with nothing worth doing it says so: a cheap, quiet run, no wasted
credit. An agent that knows when it isn't worth running.

## Anyone can try it

It's all Google Cloud — Vertex AI for the Gemini models, Cloud Run for the nightly job,
Cloud Scheduler to trigger it, BigQuery for the history, Cloud Logging for the audit trail,
Secret Manager for credentials. And there's a one-click "Open in Cloud Shell" button: deploy
the whole fleet to your own project in a few minutes, in a safe demo mode, then add your own
email and phone later. You pay only for your own usage.

## Why it matters

The interesting frontier for AI agents isn't doing *more* — it's doing the *right* things,
and being trustable with real-world actions. DuckFleet is a small, concrete answer: an
autonomous fleet that hunts hard, inside the lines. It refuses, it asks, it logs, and it
knows its own worth. It turns rubber ducks into business-class seats — and the next duck
won't get past it.

---

## NotebookLM customize prompt (paste into Audio Overview → Customize)

**Settings:** Format = **Deep dive** · Length = **Short** · one source (this file). More
sources / "Default" length = a longer episode.

> Start COLD on the rubber-duck story — your very first words must be about the $3.50 BigW
> rubber duck that stacked into a business-class seat. Do NOT open with a welcome, host
> intros, "today we're talking about," or any preamble — jump straight in. Keep the WHOLE
> thing UNDER 3 minutes: fast, punchy, no tangents or filler. Two hosts; one is a curious
> skeptic asking the questions a hackathon judge would ("but does it actually DO anything?",
> "is it really deployed?"), the other answers by example. Cover briefly, in order: a nightly
> agent fleet on Google Cloud → you set it up just by talking to it → the ranked morning
> brief → it refuses bad errands and skips what you don't want, and says why → it can place a
> GATED phone call that identifies itself as an AI → it reports its own ROI and knows when it
> isn't worth running → one-click deploy on Google Cloud. End immediately on the line: "hunts
> hard, inside the lines — the next duck won't get past it." No sign-off after that line.
