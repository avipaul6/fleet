# Deploy (all GCP, ~$0 idle)

## Services
- **Cloud Run service** `duckfleet-orchestrator` — ADK app (FastAPI via `adk api_server`), scale-to-zero.
- **Cloud Run job** `duckfleet-scouts` — optional split if scraping gets heavy; else scouts run in the orchestrator.
- **Cloud Scheduler** `nightly-hunt` (cron `0 2 * * *`, Australia/Brisbane) → **Pub/Sub** `scout-jobs` → push subscription to the orchestrator endpoint.
- **Firestore** (native mode): `offers`, `stock_signals`, `approvals`, `briefs`.
- **BigQuery** dataset `duckfleet`: `offer_history` (scout raw output, partitioned by scrape date) — analytics + the "massive dataset heavy lifting" story.
- **Cloud Logging**: structured audit events from guardrails (log name `duckfleet.audit`).
- **Secret Manager**: phone gateway creds, Gmail OAuth token.
- **Vertex AI**: Gemini (native) + Model Garden for Claude when A/B-ing via LiteLlm.
- **Conversational Agents (Dialogflow CX) Phone Gateway**: outbound stock-verification calls.

## Commands (sketch)
```bash
gcloud run deploy duckfleet-orchestrator \
  --source . --region australia-southeast1 \
  --set-env-vars-file env.yaml --no-allow-unauthenticated

gcloud pubsub topics create scout-jobs
gcloud scheduler jobs create pubsub nightly-hunt \
  --schedule "0 2 * * *" --time-zone "Australia/Brisbane" \
  --topic scout-jobs --message-body '{"run":"nightly"}'
```

## Hackathon cost control
Judging doesn't require the app live — record the demo, then
`gcloud scheduler jobs pause nightly-hunt` and let Cloud Run scale to zero.
$150 credit covers the build comfortably; Routes API + phone gateway are the
only per-use costs worth watching.
