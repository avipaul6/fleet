# DuckFleet — Project Context for Claude Code

**One-liner:** DuckFleet — an agent fleet that hunts loyalty points while you sleep,
starting with the $3.50 rubber duck that was secretly a business-class seat.

**Mascot:** 🦆 — keep it in the README and demo regardless of wordmark. The duck is the brand.

**Repo:** github.com/duckfleet/fleet  ·  **Domain:** duckfleet.dev  ·  **Identity:** duckfleet.dev@gmail.com

---

## ⭐ North star (optimise for THIS, not the contest)
This is a **public capability artifact** whose job is to credential the author as a
**governed-agentic-AI engineer**. Rank of goals:
1. Ship a packaged, public, provably-working artifact with a sharp governed-agency
   narrative by ~Aug 31.
2. Do it in public (write-up, video, clean repo) — deliberately attack distribution.
3. Hackathon placing is nice, not load-bearing. Product/market outcomes are a cheap
   option held on the side, NOT a thesis to chase.
**Trap to avoid:** don't let product/scale questions (multi-tenant hosting, real
Level-2 SaaS) eat the two weeks that belong to shipping + packaging. Those are
explicitly DEFERRED (see below).

---

## What this is
A background multi-agent fleet (Google ADK) that ingests loyalty offers + stock
signals overnight, computes offer-stacking value and cents-per-point, decides
whether an errand is worth the time/fuel, optionally verifies stock by a gated
phone call, and delivers a ranked morning action list. Built for the Google
"All Things Agentic" hackathon (Taskmaster track, submissions due Aug 31 2026).

## Locked decisions — do NOT re-litigate these
1. **Name:** DuckFleet. Tagline mandatory wherever the name appears.
2. **Track:** The Taskmaster (background agents doing heavy lifting async).
3. **Stack is 100% GCP:** Cloud Scheduler → Pub/Sub → Cloud Run (scale-to-zero),
   Firestore (state/approvals), BigQuery (offer_history — the "big data" story),
   Cloud Logging (audit), Secret Manager, Vertex AI (Gemini native + Model Garden
   for Claude), Conversational Agents / Dialogflow CX Phone Gateway (voice).
4. **Model switching is a first-class feature.** Two tiers, resolved from env by
   `agents/model_factory.py`:
   - `DUCKFLEET_MODEL_FAST` / `DUCKFLEET_MODEL_STRONG`.
   - Plain string → native Gemini via ADK.
   - `vertex_ai/...` prefix → LiteLlm wrapper (e.g. Claude on Vertex Model Garden).
   - Default to Gemini for submission (it's Google's contest); switchability is a
     talking point + lets you show cross-model eval results.
5. **Governance is a FEATURE, not a slide.** `guardrails/gates.py` enforces spend
   caps, call-hours, one-call-per-store, ToS filtering, mandatory AI
   self-identification on calls, human approval gates, structured audit log.
   The demo SHOWS the agent refusing a bad errand and asking before dialling.
   (A prior hackathon entry was a compliance agent that only *reported* — this time
   governance *acts and shows receipts*. That's the differentiator.)
6. **Division of labour rule:** the LLM FINDS stacks; deterministic Python does
   ALL arithmetic (`compute_stack_value`, `worth_it_verdict`). Never let the model
   do maths it can delegate — demo numbers must be correct.

## Runtime portability (GCP now, Claude later — same brain)
The fleet LOGIC is runtime-agnostic and is the real IP. Deployment targets are
adapters, NOT separate projects. Keep them as sibling folders in ONE repo:
- `runtimes/gcp_adk/`  — ADK + Cloud Run deployment. THE hackathon target. Build now.
- `runtimes/managed_agents/` — Claude Managed Agents target. Post-hackathon, optional.
  (Managed Agents is Claude-only + costs session-hours; it's a convenience hosting
  tier for non-technical users IF traction appears — never the spine, never for the
  GCP-required hackathon.)
Rule: never put agent/guardrail/schema logic inside a runtime folder. Runtimes only
wire the shared logic to a platform. This keeps a future Claude port a re-wire, not
a rewrite.

## Provider / bring-your-own-key abstraction
Model config per tier is `{provider, model, api_key_env}`. Keys are read ONLY from
the user's own env / Secret Manager — NEVER bundled or committed. This makes
DuckFleet shippable to strangers at $0 inference cost to the author (they bring
their key). `model_factory.py` already resolves native-Gemini vs LiteLlm; extend it
to also resolve the credential source per tier.

## Who pays for what (bake the cost boundary into the design)
- **Self-host (BYO GCP project + BYO key):** unlimited users, $0 to author. The repo.
- **Level 0 (static page + video):** ~$0, non-technical friendly, nobody "runs" it.
- **Level 1 (replay on fixtures):** ~$0, feels real — powers video + evals + demo.
- **Live demo (single fixed profile, cached + rate-limited, READ-ONLY, no calls/no
  spend):** bounded cost on author's project; the public "it really works" shopfront.
- **Real multi-tenant Level 2:** costs scale on author's bill + holds user keys →
  DEFERRED. If ever built: push cost back via BYO-project, keep read-only, never
  wire phone/spend into a public instance.
Phone gateway + Maps Routes are the only author-side per-use costs; in self-host /
demo they run in the user's / a single project. Never centralise them for strangers.

## Replay mode (one mechanism, three payoffs)
Make `--replay` a first-class run mode: agents run against a deterministic fixture
set producing a known-good brief. Powers (a) the hackathon video's guaranteed hero
stack, (b) the eval tests, (c) the Level-1/public demo. Build it early, not as an
afterthought.

## Architecture
`SequentialAgent(root)` over: `ParallelAgent(scouts)` → valuer → worth_it →
caller (gated) → presenter. State flows via ADK output_key/session state.
Coordinator deployed as Cloud Run service; Scheduler→Pub/Sub triggers nightly run.

Agents + model tiers:
- coordinator (STRONG), valuer (STRONG), caller (STRONG)
- scouts / worth_it / presenter (FAST)

## Coding conventions
- Python 3.11+, ADK (`google-adk`), Pydantic v2 for all schemas.
- Schemas in `schemas/` are the contract — lock them before adding scouts.
- Scrapers: read-only, rate-limited, respect robots.txt. Prefer stable feeds
  (OzBargain RSS) over brittle HTML. Say this in the video.
- Every real-world action routes through a guardrail gate. No exceptions.
- Tests in `evals/` are red-team failure-mode checks; keep them green, they're
  demo receipts and CI.

## Repo map (target)
```
duckfleet/
  agents/            # fleet logic — runtime-agnostic (the real IP)
  schemas/           # Offer / StockSignal / ActionItem contracts
  guardrails/        # governance — runtime-agnostic
  evals/             # red-team failure-mode harness
  fixtures/          # seeded offers incl. the hero "duck" stack (powers replay)
  runtimes/
    gcp_adk/         # ADK + Cloud Run (hackathon target — build now)
    managed_agents/  # Claude Managed Agents (later, optional)
  config/            # settings via env
  deploy/            # Cloud Run / Scheduler / Pub/Sub
  demo/gcp-hackathon/  # DEMO_SCRIPT.md, PLAN.md — hackathon-specific material
  devlog/            # dated build log + design rationale (kept out of README)
  CLAUDE.md  README.md  LICENSE  .gitignore
```

## Out of scope (state this in README — scoping is judged)
- Loyalty-account OAuth/linking (hardcode household profile in config).
- Any automated purchasing or points-redemption booking.
- More than ~3 scouts. Mobile app. Real multi-tenant hosting.

## First tasks in Claude Code
1. Add `.gitignore` (Python) + `LICENSE` (MIT). Commit the scaffold as first commit,
   push to github.com/duckfleet/fleet.
2. Reshape into the repo map above: move ADK/Cloud-Run specifics under
   `runtimes/gcp_adk/`; keep agents/schemas/guardrails runtime-agnostic. Add
   `fixtures/` with the hero duck stack.
3. `pip install -r requirements.txt`; get `adk web` running the coordinator with
   ONLY the OzBargain scout end-to-end. Prove the toolchain before adding breadth.
4. Wire `--replay` against fixtures so a known-good brief renders with no live calls.

## Riskiest item
Phone gateway (Dialogflow CX). Timebox to 3 days. Fallback: simulated call with
real TTS audio, clearly labelled "simulated". Honesty > fakery on video.

## Verify before relying on (post-cutoff, check docs)
Google ADK API surface, Gemini model IDs, Claude-on-Vertex model IDs, Managed Agents
pricing/beta status. Confirm against official docs (ai.google.dev, cloud.google.com,
docs.claude.com) — training data may be stale.

---

## CURRENT STATUS & HANDOFF (as of ~2026-08-21)

**Built & working (all end-to-end, tested):**
- Orchestrator `agents/fleet.py::run_fleet(replay)` chains: get offers (live OzBargain
  scout OR `fixtures/replay_offers.json`) → **ToS gate** → deterministic valuation +
  **spend gate** → **preference gate** (avoid / conditional; honest skip reasons) →
  worth-it (real Maps Routes, or frozen drive in replay) → **presenter** → BigQuery +
  audit + email. Returns brief + assessed + audit + economics + call_candidates.
- Agents: `scout_ozbargain`, `valuer` (+`compute_stack_value`), `worth_it` (+`errand_cost`
  real Routes), `presenter`, `caller` (gated), `onboarding` (chat → `profile.json`).
- Guardrails (`guardrails/gates.py`): gate_tos, gate_spend, gate_preference,
  gate_phone_call, gate_call_script (AI self-ID), audit trail (`record`/`audit_trail`).
- Gated phone call: `agents/verification.py` — real **Twilio** call (via TwiML Bin URL on
  trial) + real **Cloud Text-to-Speech** audio; every gate enforced. Confirmed a real call.
- Email: `agents/delivery.py` — multipart **HTML + plain-text**; points-first display,
  honest skip reasons, **Activate/view + 📅 Google Calendar reminder** links, run-ROI line,
  "what's real vs simulated" provenance. Real Gmail send works.
- Cost self-governance: `agents/economics.py` — per-run cost vs value + ROI verdict.
- History: `agents/history.py` — appends to BigQuery `duckfleet.offer_history`.
- Evals: 18 red-team tests green (`python -m evals.run`).
- Dev runners: `scripts/dev_{fleet,scout,valuer,worth_it,caller,replay}.py`; `adk web adk_apps`
  (scout/valuer/worth_it/presenter/onboarding apps).

**Deployed on GCP (project `duckfleet-agents`, region us-central1, Vertex location=global):**
- Cloud Run **Job** `duckfleet-nightly` (deploy: `runtimes/gcp_adk/deploy.sh`), scheduled
  02:00 Australia/Brisbane via Cloud Scheduler `nightly-hunt` (`schedule.sh`).
- Model: **both tiers `gemini-3.7-flash`** (newest GA; no 3.x Pro available to the project —
  3-pro/3.5-pro 404). `.env` local + deploy.sh both set it.
- Secrets in Secret Manager: `duckfleet-gmail-{client-id,client-secret,refresh-token}`.
  Twilio creds are laptop-only (calls are approval-triggered, not in the headless nightly).
- BigQuery sink on (`DUCKFLEET_BIGQUERY_DATASET=duckfleet`).
- One-click deploy: README "Open in Cloud Shell" badge → `runtimes/gcp_adk/{tutorial.md,quickstart.sh}`.
- **`.env` is laptop-only** (gitignored); the cloud job's config = deploy.sh env vars +
  Secret Manager. A redeploy (`deploy.sh`) is required to push code/config changes to the nightly.

**Docs/submission:** README refreshed (accurate, flash/pro wording, no "$0" claims);
`docs/architecture.svg` (GCP-styled, accurate); demo materials in `demo/gcp-hackathon/`:
`DEMO_SCRIPT.md` (podcast-style beat sheet), `PODCAST_SOURCE.md` (NotebookLM source + prompt —
already generated a good ~2.5-min episode), `SHOT_LIST.md` (what to record).

**What's LEFT (hackathon, due 2026-08-31):**
1. Record the demo video (InShot; podcast audio + shot-list clips + Veo cold-open of the
   duck→business-class; add "BigW/Australia" as text overlays — Veo garbles logos).
2. Devpost write-up (problem/solution/how-built/challenges/what's next) + submit.
3. Bonus points: publish the NotebookLM podcast; #AllThingsAgentic on social.

**Roadmap (post-hackathon, real-life):**
- **Shopping-habits valuation** (bounded, high value): add `regular_merchants` to profile;
  in `_value()` treat spend-you'd-make-anyway as free → fixes Flybuys/EDR "spend $X get pts"
  offers valuing to $0. This is the real fix behind the honest-reasons patch.
- Online vs in-store `fulfilment` flag (no drive penalty for online).
- **Behaviour-learning agent** — adapts the profile from feedback/behaviour over time.
- Redemption-side ("where can my points take me") — see `devlog/2026-08-19-roadmap-redemption.md`.
- Loyalty-account actuation (auto-activate boosts) — needs auth/ToS review; user-session only.

**Working preferences:** user drives all commits/pushes (do NOT commit); prefers fixing
root cause over workarounds; keep public voice reading as a real project, not hackathon-only.
