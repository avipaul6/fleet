#!/usr/bin/env bash
# DuckFleet one-click quickstart — run in Google Cloud Shell.
# Deploys the nightly fleet as a Cloud Run Job in REPLAY mode (deterministic hero brief,
# NO secrets required) and runs it once so you can see the brief it produces.
# Runs on your own project — you pay for your own usage (scale-to-zero idle; a run is cents).
# Add Gmail/Twilio + a nightly schedule later (see runtimes/gcp_adk/README.md).
set -euo pipefail

PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
if [ -z "${PROJECT}" ] || [ "${PROJECT}" = "(unset)" ]; then
  echo "No project selected. Run:  gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi
REGION="${REGION:-us-central1}"
JOB=duckfleet-nightly
echo "Project: ${PROJECT}  |  Region: ${REGION}"

echo "== Enabling APIs (first run can take a minute)…"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com aiplatform.googleapis.com --project "${PROJECT}" -q

SA="$(gcloud iam service-accounts list --project "${PROJECT}" \
      --format='value(email)' --filter='displayName:Compute Engine default')"
echo "== Granting Cloud Build + Vertex AI to ${SA}…"
for r in roles/cloudbuild.builds.builder roles/aiplatform.user; do
  gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${SA}" --role="${r}" --condition=None -q >/dev/null
done

echo "== Building + deploying the Cloud Run Job (REPLAY mode)…"
gcloud run jobs deploy "${JOB}" --source . --region "${REGION}" --project "${PROJECT}" --quiet \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=global,DUCKFLEET_PROJECT_ID=${PROJECT},DUCKFLEET_REGION=${REGION},DUCKFLEET_MODEL_FAST=gemini-3.5-flash,DUCKFLEET_MODEL_STRONG=gemini-3.5-flash,DUCKFLEET_REPLAY=true"

echo "== Running the fleet once…"
gcloud run jobs execute "${JOB}" --region "${REGION}" --project "${PROJECT}" --wait

echo
echo "✅ Done! DuckFleet ran on your project. See the morning brief it produced:"
echo
gcloud logging read 'resource.type=cloud_run_job AND resource.labels.job_name=duckfleet-nightly' \
  --project "${PROJECT}" --limit 20 --freshness=5m --format='value(textPayload)' 2>/dev/null \
  | grep -m1 fleet_run_complete || echo "(logs may take a few seconds — re-run the command above)"
echo
echo "Next: add Gmail delivery + Twilio calls + a nightly schedule — see runtimes/gcp_adk/README.md"
