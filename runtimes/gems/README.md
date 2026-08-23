# Onboarding as a Gemini Gem 🦆

A **Gem** is a custom version of Gemini — instructions plus reference files — that lives
inside the Gemini app you already have. This folder packages DuckFleet's onboarding as a
Gem so a non-technical user can set their profile **by chatting in Gemini**, instead of
running `adk web` locally.

It's an additive *surface*, not new logic. The onboarding brain
([agents/onboarding.py](../../agents/onboarding.py)) and the ADK web app
([adk_apps/onboarding](../../adk_apps/onboarding)) still work for developers. Per the
runtime-portability rule, no agent logic lives here — a Gem is just another adapter that
produces the same [`profile.json`](../../schemas/profile.py) contract the fleet reads.

## Why a Gem (vs. the ADK web app)

| | ADK web app | This Gem |
|---|---|---|
| Where it runs | your laptop (`adk web adk_apps`) | the Gemini app you already use |
| Needs a Python env | yes | no |
| Cost to you (the author) | your inference | **$0** — runs on the user's own Gemini |
| Audience | developers | anyone |

The Gem doesn't touch your GCP deployment. It produces a valid `profile.json`; you drop
that file into your deployment and the next nightly run picks it up. That keeps onboarding
zero-infrastructure and matches DuckFleet's BYO / self-host cost model.

## Install (once, ~2 minutes)

1. Open the **Gemini app** → **Gems** → **New Gem** (Gem manager).
2. **Name:** `DuckFleet Onboarding`
3. **Instructions:** paste the entire contents of
   [`onboarding_gem_instructions.md`](onboarding_gem_instructions.md).
4. **Knowledge:** upload [`profile_schema.md`](profile_schema.md) as a knowledge file so
   the Gem always emits a schema-valid profile.
5. Save.

## Use

1. Open the `DuckFleet Onboarding` Gem and describe your household in plain language —
   e.g. *"Qantas and Flybuys, no more credit cards, I'd switch electricity for good
   points, $100 a week, brief me at me@example.com, I'm in Bondi 2026."*
2. It confirms in one line and hands you a `profile.json` code block.
3. Save that block as `profile.json` in the root of your DuckFleet deployment (next to
   `README.md`). If you deployed via the Cloud Shell one-click button, upload it there and
   redeploy with [`runtimes/gcp_adk/deploy.sh`](../gcp_adk/deploy.sh). The next nightly run
   reads it automatically ([config/settings.py](../../config/settings.py)).

Re-chat with the Gem any time to update your preferences — just replace the file.

## Keeping this in sync

The instructions and schema here mirror [schemas/profile.py](../../schemas/profile.py) and
the mappings in [agents/onboarding.py](../../agents/onboarding.py). If the `Profile` schema
changes (new program, new category), regenerate the JSON Schema block in
[`profile_schema.md`](profile_schema.md) with:

```bash
python -c "import json; from schemas.profile import Profile; print(json.dumps(Profile.model_json_schema(), indent=2))"
```
