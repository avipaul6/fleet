# DuckFleet 🦆✈️

**A background agent fleet that turns rubber ducks into business-class seats.**

In 2025, a $3.50 BigW rubber duck — stacked across promotions — earned Qantas Points at
0.59c/point. The only people who caught it were forum addicts refreshing OzBargain.
DuckFleet is a fleet of agents that hunts the next duck while you sleep: it ingests
offers and stock signals overnight, does the stacking math, computes whether the errand
is worth your time and petrol, phones the store to verify stock (with your approval),
and hands you a ranked action list with your morning coffee.

**Track:** The Taskmaster — background agents that handle the heavy lifting asynchronously.

---

## Architecture (100% GCP)

```mermaid
flowchart TD
    CS[Cloud Scheduler<br/>nightly + 6-hourly] -->|trigger| PS[(Pub/Sub<br/>scout-jobs)]
    PS --> SR[Cloud Run Jobs<br/>Scout Fleet]
    SR -->|normalised Offer JSON| FS[(Firestore<br/>offers / stock / profile)]
    SR -->|raw history| BQ[(BigQuery<br/>offer_history)]
    FS --> ORCH[Cloud Run Service<br/>ADK Orchestrator]
    ORCH --> VAL[Valuer Agent<br/>stacking math, c/point]
    ORCH --> GEO[Worth-It Agent<br/>Routes API: time+fuel vs value]
    ORCH --> CALL[Caller Agent<br/>Conversational Agents<br/>Phone Gateway - GATED]
    ORCH --> PRES[Presenter Agent<br/>morning brief via Gmail API]
    GR[Guardrails Layer<br/>spend cap · call policy · approval gate · audit log] -.wraps.- ORCH
    ORCH -->|audit events| CL[(Cloud Logging<br/>audit trail)]
```

**Agent fleet (ADK, Python):**

| Agent | Job | Model tier |
|---|---|---|
| `coordinator` | Root orchestrator; sequences the pipeline, owns state | STRONG |
| `scout_pointhacks`, `scout_ozbargain`, `scout_stock` | Parallel ingestion → normalised `Offer` schema | FAST |
| `valuer` | Stack detection, cents-per-point, expected value | STRONG |
| `worth_it` | Drive time + fuel + time-value vs. item value; can REFUSE | FAST |
| `caller` | Voice stock-verification via phone gateway — human-gated | STRONG |
| `presenter` | Ranked morning action list | FAST |

**Governance is a feature, not a slide:** every real-world action (call, purchase
suggestion above cap) passes through `guardrails/gates.py` — spend caps, one-call-per-
store policy, AI self-identification script, human approval gate, structured audit log
to Cloud Logging. The demo shows the agent *refusing* an errand that isn't worth the
drive and *asking permission* before dialling.

---

## Model switching

Every agent takes its model from config, resolved by `agents/model_factory.py`:

- Plain model string (e.g. `gemini-3.5-flash`) → native ADK/Gemini path.
- Prefixed string (e.g. `vertex_ai/claude-sonnet-4-5`) → wrapped in ADK's `LiteLlm`
  adapter, still running through **Vertex AI Model Garden** — so you can A/B Gemini vs
  Claude *without leaving GCP*, per agent tier, via env vars:

```bash
export DUCKFLEET_MODEL_FAST="gemini-3.5-flash"
export DUCKFLEET_MODEL_STRONG="gemini-2.5-pro"
# swap the valuer to Claude on Vertex for an eval run:
export DUCKFLEET_MODEL_STRONG="vertex_ai/claude-sonnet-4-5"
```

Gemini is the configured default. Design rationale and model-choice notes live in
[`devlog/`](devlog/).

---

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # set project, models, home location, caps
adk web                      # local dev UI — run the coordinator interactively
python -m evals.run          # red-team the fleet against failure modes
```

Deploy: see `deploy/README.md` (Cloud Run + Scheduler + Pub/Sub, ~$0 idle).

## Repo map

```
agents/          fleet definitions + tools
schemas/         Offer / StockSignal / ActionItem (Pydantic, the contract)
guardrails/      gates, caps, call policy, audit
evals/           failure-mode harness (duck-hoarding, ToS, rogue-call)
fixtures/        seeded offers incl. the hero "duck" stack (powers replay)
config/          settings via env
deploy/          Cloud Run / Scheduler / Pub/Sub setup
demo/            how to see it working (gcp-hackathon/: DEMO_SCRIPT, PLAN)
devlog/          dated build log + design rationale
```
