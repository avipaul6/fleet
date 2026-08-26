## 🦆 DuckFleet — an agent fleet that hunts loyalty points while you sleep

### What inspired it

It started with a rubber duck. In 2025 a **$3.50 bath toy at Big W** became briefly famous in
Australian bargain circles: bought in bulk and stacked across promotions — a store bonus, a
shopping-portal multiplier, a card offer — it earned Qantas Points at about half a cent each.
Do the maths and that pile of $3.50 ducks was, effectively, a **business-class seat**.

The catch: the only people who caught it were forum obsessives refreshing OzBargain at
midnight. The value is real, but capturing it is a tedious, full-time hunt. Who actually has
time for that? **Basically nobody.**

That's the itch DuckFleet scratches — hunt the next duck automatically, overnight, while you
sleep. But the interesting problem isn't "find deals." It's building an agent you can *trust
with real-world actions*. So DuckFleet's whole personality is **restraint**.

### What it does

Every night a **Cloud Run Job** wakes up and a fleet of agents does the heavy lifting: scouts
read the deal feeds, a valuer does the stacking maths (cents-per-point), a *worth-it* agent
weighs drive time and petrol against the reward, and a presenter emails you a ranked morning
brief. You wake up to a short list of what's **actually worth doing** — and, just as
importantly, **what to skip and why**.

The part that makes it *not a newsletter*: it **decides, refuses, and acts**, under governance.

- **It refuses bad errands.** 40 minutes for a $6 toy? Skip — and it says why.
- **It respects your limits.** Tell it "no more credit cards" and it ignores a card worth
  ~$1,600 in nominal points, and tells you it did.
- **It's honest about the boring stuff.** Instead of a confabulated "no points" excuse it gives
  the real reason — *"Velocity isn't a program you collect"*, or *"only worth it if you'd
  already spend $50 at Coles anyway."*
- **It can act — carefully.** If a deal depends on stock, it can **call the store** to check —
  but only after you approve, only within calling hours, only once per store, and it **opens
  the call by identifying itself as an AI**. You hear a real phone ring and a real voice say,
  *"Hi, I'm an AI assistant calling on behalf of a customer."*
- **It governs its own cost.** Each run it tallies compute spent against value surfaced and
  reports the ROI — and on a quiet night with nothing worth doing, it says so.

### How we built it

**100% Google Cloud** (telephony via Twilio is the only non-GCP piece):

- **Vertex AI (Gemini)** for the agents, via the **Google Agent Development Kit (ADK)**
- **Cloud Scheduler → Cloud Run Job** for the nightly, scale-to-zero background run
- **Maps Routes API** for real drive-time economics, **Cloud Text-to-Speech** for the call audio
- **BigQuery** for offer history, **Cloud Logging** for the governance audit trail,
  **Secret Manager** for credentials
- **Pydantic v2** schemas as the contract; a `SequentialAgent` over a `ParallelAgent` of scouts

The core design rule: **the LLM finds the stack; deterministic Python does all the arithmetic.**
Demo numbers must be correct, so the model never does maths it can delegate. Given an offer with
base points $p$ and stacking multipliers $m_1, m_2, \dots$, the valuer computes:

$$P_{\text{total}} = p \prod_i m_i, \qquad
c_{\text{point}} = \frac{\text{price}}{P_{\text{total}}}\times 100 \ \text{(¢/pt)}, \qquad
V_{\text{net}} = P_{\text{total}}\cdot \frac{v_{\text{program}}}{100} - \text{price}$$

The *worth-it* gate then subtracts the real cost of the errand before anything reaches you:

$$V_{\text{after trip}} = V_{\text{net}} - \underbrace{\frac{t}{60}\,r_{\text{time}}}_{\text{time}}
- \underbrace{d\,\cdot f}_{\text{fuel}}, \qquad
\text{verdict} = \begin{cases} \textbf{do it} & V_{\text{after trip}} > 0\\[2pt] \textbf{skip} & \text{otherwise}\end{cases}$$

And the fleet applies the same test to *itself* — ROI $= V_{\text{surfaced}} / C_{\text{compute}}$
— so it knows when it wasn't worth running.

Governance isn't a slide; it's code. Every real-world action routes through a guardrail gate in
`guardrails/gates.py`: ToS filtering, spend caps, preference skips, one-call-per-store,
call-hours, mandatory AI self-identification, and a structured audit log. A **`--replay` mode**
runs the whole fleet against deterministic fixtures, which powers the demo, the eval suite, and
a hosted **"email me a sample brief"** page — scan a QR, no install. Setup is conversational: you
tell an onboarding agent *"I collect Qantas and Flybuys, no more credit cards, $100 a week"* and
it writes your profile. And anyone can deploy the whole thing to their **own** Google Cloud with
a one-click **Open in Cloud Shell** button — you bring your own project and key, so it's $0 to us
and private to you.

### What we learned

- **Governance is a feature, not a constraint.** The moments the demo audience remembered were
  the agent saying *no* — refusing a drive, skipping a card, asking before dialling. Agency you
  can trust is more compelling than agency that just does more.
- **Delegate the maths.** Keeping every number in deterministic Python (not the LLM) is what
  makes the output trustworthy — and made red-team eval tests trivial to keep green.
- **Honesty reads as quality.** Real skip reasons beat confabulated ones; labelling the
  re-enacted store call as *simulated* (the audio is real, the shop worker is a dramatisation)
  made the whole thing *more* credible, not less.
- **Runtime-agnostic logic is the real IP.** Agents, schemas, and guardrails stay platform-free;
  deployment targets are thin adapters, so a future port is a re-wire, not a rewrite.

### Challenges we faced

- **The phone gateway was the riskiest piece.** We timeboxed it and landed a real, gated Twilio
  call with real Cloud TTS audio — every guardrail enforced, including AI self-identification.
- **Honest reasons vs. confabulation.** Early briefs invented "no points" excuses; we replaced
  that with real logic (uncollected program, spend-you-wouldn't-make, drive-not-worth-it).
- **Correct numbers under a live model.** Solved by the LLM-finds / Python-computes split.
- **Staying honest on camera.** Veo garbles logos, so brand names are text overlays; the store
  call is clearly labelled a dramatisation of the genuine automated call.
- **Scoping discipline.** We deliberately deferred multi-tenant hosting, loyalty-account OAuth,
  and any automated purchasing — governed agency, done well and honestly, over feature sprawl.

### What's next

- **Shopping-habits valuation** — treat spend you'd make anyway as "free," fixing the
  spend-$X-get-points offers that currently under-value.
- A **behaviour-learning agent** that adapts the profile from your feedback over time.
- **Redemption-side** hunting ("where can my points actually take me").
- **Model portability** — the same brain on Claude via Vertex Model Garden (model switching is
  already a first-class feature).

DuckFleet is a small, concrete answer to the real frontier for AI agents: not doing *more*, but
doing the *right* things and being trustable with real-world actions. It hunts hard, inside the
lines. **The next duck won't get past it.**
