# Demo

Everything needed to *see* DuckFleet working, without a live GCP run.

- **`gcp-hackathon/`** — material specific to the "All Things Agentic" hackathon submission:
  - `DEMO_SCRIPT.md` — 3-minute video beat sheet.
  - `PLAN.md` — the build cut / timeline.

## Ready-to-see demo (replay mode) — coming with the scout work

The self-contained demo runs the real fleet against deterministic fixtures
(`fixtures/hero_duck.json`) so it always produces the known-good "hero duck" brief —
no live scraping, no model cost, no phone calls. Once `--replay` lands, this folder will
document the one command to render that brief. See the devlog for status.
