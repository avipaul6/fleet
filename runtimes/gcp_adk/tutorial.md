# Deploy DuckFleet 🦆

<walkthrough-author name="DuckFleet" repositoryUrl="https://github.com/duckfleet/fleet"></walkthrough-author>

## Welcome

**DuckFleet** is a governed agent fleet that hunts loyalty-point deals overnight, does the
stacking maths, refuses errands that aren't worth the drive, respects your preferences, and
can place a *gated* phone call to verify stock — then emails you a ranked morning brief.

This walkthrough deploys it to **your** Google Cloud project in **replay mode**: a
deterministic demo brief with **no secrets required**. It runs on your own project, so
you pay for your own usage — the job scales to zero when idle and a run costs cents.

Estimated time: **~5 minutes**. Click **Start**.

## Pick a project

<walkthrough-project-setup></walkthrough-project-setup>

DuckFleet will deploy to the project selected above.

## Deploy the fleet

Run the quickstart — it enables the required APIs, grants the minimal roles, builds the
container, deploys the Cloud Run Job, and runs it once:

```bash
bash runtimes/gcp_adk/quickstart.sh
```

<walkthrough-footnote>The first run builds a container image, so give it a couple of minutes.</walkthrough-footnote>

## See the brief

The command above prints a run summary. To read the full brief any time:

```bash
gcloud logging read 'resource.type=cloud_run_job' --limit 20 --freshness=10m --format='value(textPayload)'
```

You'll see the ranked brief: a top pick, principled skips, anything excluded for ToS risk,
and the run's own ROI.

## What next

- **Email the brief** — add Gmail credentials (`runtimes/gcp_adk/README.md`).
- **Real phone calls** — add Twilio credentials.
- **Nightly schedule** — `bash runtimes/gcp_adk/schedule.sh`.
- **Live deals** — redeploy with `DUCKFLEET_REPLAY=false`.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

You've deployed a governed agent fleet to your own cloud. 🦆
