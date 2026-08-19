# Devlog — 2026-08-19 · Foundations & GCP connection

Running log of build decisions and the *why* behind them. Keeps rationale and
asides out of the README (which should read as product docs, not a diary).

## GCP identity & connection
- Project: **`duckfleet-agents`** under the `duckfleet.dev` account, kept isolated from
  the personal Google account via a dedicated gcloud config dir (`CLOUDSDK_CONFIG`).
- Auth: **Vertex AI + Application Default Credentials** — no key files in the repo.
- Region: **`us-central1`** everywhere (Australia regions lag on model/feature
  availability, and there's no data-residency constraint). Nightly Scheduler keeps the
  `Australia/Brisbane` timezone so the brief lands at the user's local morning.

## Model tiers — verified live against the project (not trusted from the scaffold)
Probed real model IDs in `duckfleet-agents`:
- **FAST = `gemini-3.5-flash`** — newest GA, agentic-tuned. Requires Vertex `location=global`.
- **STRONG = `gemini-2.5-pro`** — best Pro available to the project (Gemini 3.x Pro is
  preview/allowlist, returns 404). ⚠️ `gemini-2.5-pro` is scheduled to sunset **2026-10-20**;
  swap to a 3.x Pro when the project gets access.
- The scaffold's `gemini-3.5-pro` does **not** exist — corrected in `config/settings.py`.

## Model switching (design rationale — moved here from the README)
Model per tier is resolved by `agents/model_factory.py` from env vars
(`DUCKFLEET_MODEL_FAST` / `DUCKFLEET_MODEL_STRONG`):
- Plain string → native Gemini via ADK.
- `vertex_ai/...` prefix → wrapped in ADK's `LiteLlm`, still via Vertex Model Garden
  (e.g. Claude on Vertex) — so you can A/B Gemini vs Claude **per tier without leaving GCP**.

Why it matters: switchability lets us show cross-model eval results, and it's what makes
the fleet portable to a non-GCP runtime later (the logic is the IP; the model + runtime
are adapters). Gemini stays the configured default.

## Toolchain proof
Python 3.12 venv (3.14 lacked wheels + local clang is broken), deps installed via `uv`,
full scaffold imports clean against `google-adk 2.7.1`, and an end-to-end ADK → Gemini →
Vertex smoke test returned a real response. PLAN Day 1–3 milestone cleared.

## Open architectural question (see also deploy notes)
Whether to deploy on **Vertex AI Agent Engine** (managed runtime: sessions + memory bank,
one-command deploy) vs **Cloud Run** (scale-to-zero, self-managed session service). Leaning
Agent Engine as more on-theme for the "All Things Agentic" track; it's a deploy-adapter
choice that doesn't affect the runtime-agnostic agent logic. Decide at deploy phase.
