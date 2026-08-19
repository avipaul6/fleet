# Runtime: GCP (Cloud Run Job + Scheduler)

The nightly fleet as a **Cloud Run Job** (batch, scale-to-zero) fired by **Cloud
Scheduler**. This folder is a thin adapter — `job.py` just calls `agents.fleet.run_fleet()`.

## Prereqs (one-time)
The job runs as a service account that must call Vertex AI + Routes:
```bash
PROJECT=duckfleet-agents
SA=$(gcloud iam service-accounts list --project $PROJECT --format='value(email)' --filter='displayName:Compute Engine default')
gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$SA" --role=roles/aiplatform.user
# Routes API + build/run APIs:
gcloud services enable run.googleapis.com cloudbuild.googleapis.com cloudscheduler.googleapis.com
```

## Deploy the job
```bash
gcloud run jobs deploy duckfleet-nightly --source . --region us-central1 \
  --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=duckfleet-agents,GOOGLE_CLOUD_LOCATION=global,DUCKFLEET_PROJECT_ID=duckfleet-agents,DUCKFLEET_REGION=us-central1,DUCKFLEET_MODEL_FAST=gemini-3.5-flash,DUCKFLEET_MODEL_STRONG=gemini-2.5-pro,DUCKFLEET_REPLAY=true
```
(`DUCKFLEET_REPLAY=true` for a safe deterministic first run; flip to `false` for live scouting.)

## Smoke test
```bash
gcloud run jobs execute duckfleet-nightly --region us-central1 --wait
# then read the structured brief line from logs:
gcloud run jobs executions logs read --job duckfleet-nightly --region us-central1 --limit 50
```

## Schedule nightly (02:00 Australia/Brisbane)
```bash
gcloud scheduler jobs create http nightly-hunt --location us-central1 \
  --schedule="0 2 * * *" --time-zone="Australia/Brisbane" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/duckfleet-agents/jobs/duckfleet-nightly:run" \
  --http-method=POST \
  --oauth-service-account-email=$SA
```

## Cost control
Cloud Run Jobs bill only while running (a nightly run is seconds–minutes). Pause with
`gcloud scheduler jobs pause nightly-hunt`. Routes API + (later) phone gateway are the
only per-use costs to watch.

## Later
- Gmail delivery: presenter `gmail_send` tool + a `gmail.send` OAuth token in Secret Manager.
- Firestore/BigQuery sinks for state + `offer_history`.
