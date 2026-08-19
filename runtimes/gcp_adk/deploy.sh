#!/usr/bin/env bash
# Deploy the DuckFleet nightly fleet as a Cloud Run Job. Run from the repo root:
#   bash runtimes/gcp_adk/deploy.sh
#
# Prereqs (one-time, done by you in the console / earlier):
#   - Secret Manager secrets exist: DUCKFLEET_GMAIL_CLIENT_ID,
#     DUCKFLEET_GMAIL_CLIENT_SECRET, DUCKFLEET_GMAIL_REFRESH_TOKEN
#   - .env has DUCKFLEET_NOTIFY_EMAIL and DUCKFLEET_GMAIL_SENDER (non-secret)
set -euo pipefail

export CLOUDSDK_CONFIG="${CLOUDSDK_CONFIG:-$HOME/.config/gcloud-duckfleet}"
PROJECT=duckfleet-agents
REGION=us-central1
JOB=duckfleet-nightly
REPLAY="${DUCKFLEET_REPLAY:-false}"   # false = live hunt; set true for the hero-duck demo brief

# Non-secret Gmail config (read from .env; never echoed)
NOTIFY_EMAIL=$(grep -E '^DUCKFLEET_NOTIFY_EMAIL=' .env | head -1 | cut -d= -f2-)
SENDER=$(grep -E '^DUCKFLEET_GMAIL_SENDER=' .env | head -1 | cut -d= -f2-)
: "${NOTIFY_EMAIL:?set DUCKFLEET_NOTIFY_EMAIL in .env}"

SA=$(gcloud iam service-accounts list --project "$PROJECT" \
      --format='value(email)' --filter='displayName:Compute Engine default')
echo "Runtime service account: $SA"

echo "== IAM: Vertex + Secret Manager access =="
gcloud projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:$SA" --role=roles/aiplatform.user --condition=None -q >/dev/null
for s in duckfleet-gmail-client-id duckfleet-gmail-client-secret duckfleet-gmail-refresh-token; do
  gcloud secrets add-iam-policy-binding "$s" --project "$PROJECT" \
    --member="serviceAccount:$SA" --role=roles/secretmanager.secretAccessor -q >/dev/null
done

echo "== Deploy Cloud Run Job (REPLAY=$REPLAY) =="
gcloud run jobs deploy "$JOB" --source . --region "$REGION" --project "$PROJECT" \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=$PROJECT,GOOGLE_CLOUD_LOCATION=global,DUCKFLEET_PROJECT_ID=$PROJECT,DUCKFLEET_REGION=$REGION,DUCKFLEET_MODEL_FAST=gemini-3.5-flash,DUCKFLEET_MODEL_STRONG=gemini-2.5-pro,DUCKFLEET_REPLAY=$REPLAY,DUCKFLEET_GMAIL_SENDER=$SENDER,DUCKFLEET_NOTIFY_EMAIL=$NOTIFY_EMAIL" \
  --set-secrets="DUCKFLEET_GMAIL_CLIENT_ID=duckfleet-gmail-client-id:latest,DUCKFLEET_GMAIL_CLIENT_SECRET=duckfleet-gmail-client-secret:latest,DUCKFLEET_GMAIL_REFRESH_TOKEN=duckfleet-gmail-refresh-token:latest"

echo "== Smoke test: run once now =="
gcloud run jobs execute "$JOB" --region "$REGION" --project "$PROJECT" --wait

echo "Done. Schedule it nightly with: bash runtimes/gcp_adk/schedule.sh"
