# 2.5-Week Cut (submit by Aug 31)

## Days 1–3 (this week): foundations
- GEAR labs: ADK basics, MCP/tools, memory-state, structured JSON output.
- Repo scaffold running locally: coordinator + ONE scout (OzBargain RSS,
  easiest legal scrape) end-to-end with `adk web`. Schema locked.
- Guardrails module + pytest evals green (they're pure python — free win).

## Days 4–7: the fleet
- Second scout (Everyday Rewards boosts — fixture-backed is fine).
- Stock scout against one retailer's per-store availability.
- Valuer with deterministic stack math tool; seed a synthetic "duck" fixture
  so the demo has a guaranteed hero stack regardless of live deals.
- Firestore + BigQuery sinks. Deploy to Cloud Run, Scheduler firing nightly.

## Days 8–11: the showpieces
- Worth-It agent + Routes API. Map visual for the refusal beat.
- Caller: approval flow (Firestore doc + simple web/CLI approve) + phone
  gateway happy path. THIS IS THE RISKIEST ITEM — timebox to 3 days; fallback
  is a simulated call with real TTS audio, clearly labelled "simulated" (still
  demos the gate + script; honesty > fakery).
- Presenter + Gmail brief.

## Days 12–14: ship
- Architecture diagram (polish the mermaid), README pass, license file.
- Record demo: fleet-logs b-roll, BigQuery shot, refusal map, THE CALL,
  brief. Script per DEMO_SCRIPT.md. Two evenings for edit.
- Devpost write-up + submit with 48h buffer.

## Explicitly out of scope (write this in the README — scoping is judged)
- Loyalty-account OAuth/linking. Any automated purchasing. More than 3 scouts.
- Points-redemption booking. Mobile app.
