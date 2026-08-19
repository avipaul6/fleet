"""BigQuery sink — appends each run's assessed offers to <dataset>.offer_history.

The "big data heavy lifting" story: history accumulates across nights for analytics
(cents-per-point distributions, which merchants pay, verdict trends). Runtime-agnostic
and BEST-EFFORT: a sink failure is logged and swallowed — it never breaks the brief.
Enabled by setting DUCKFLEET_BIGQUERY_DATASET; disabled (no-op) when blank.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from config.settings import settings

log = logging.getLogger("duckfleet.history")

_TABLE = "offer_history"


def bigquery_enabled() -> bool:
    return bool(settings.bigquery_dataset)


def _schema():
    from google.cloud import bigquery
    F = bigquery.SchemaField
    return [
        F("run_ts", "TIMESTAMP"), F("mode", "STRING"),
        F("offer_id", "STRING"), F("merchant", "STRING"), F("item", "STRING"),
        F("program", "STRING"), F("units", "INTEGER"), F("spend_aud", "FLOAT"),
        F("total_points", "INTEGER"), F("cents_per_point", "FLOAT"),
        F("offer_value_aud", "FLOAT"), F("net_value_aud", "FLOAT"),
        F("verdict", "STRING"), F("tos_risk", "STRING"), F("audit_ref", "STRING"),
    ]


def _ensure_table(client) -> str:
    from google.cloud import bigquery
    ds_id = f"{settings.project_id}.{settings.bigquery_dataset}"
    client.create_dataset(bigquery.Dataset(ds_id), exists_ok=True)
    table_id = f"{ds_id}.{_TABLE}"
    table = bigquery.Table(table_id, schema=_schema())
    table.time_partitioning = bigquery.TimePartitioning(field="run_ts")  # partitioned by run date
    client.create_table(table, exists_ok=True)
    return table_id


def record_run(assessed: list[dict], mode: str) -> int:
    """Append the assessed offers to BigQuery. Returns rows written (0 on skip/failure)."""
    if not bigquery_enabled() or not assessed:
        return 0
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=settings.project_id)
        table_id = _ensure_table(client)
        ts = datetime.now(timezone.utc).isoformat()
        rows = [{
            "run_ts": ts, "mode": mode,
            "offer_id": a.get("id"), "merchant": a.get("merchant"), "item": a.get("item"),
            "program": a.get("program"), "units": a.get("units"), "spend_aud": a.get("spend_aud"),
            "total_points": a.get("total_points"), "cents_per_point": a.get("cents_per_point"),
            "offer_value_aud": a.get("offer_value_aud"), "net_value_aud": a.get("net_value_aud"),
            "verdict": a.get("verdict"), "tos_risk": a.get("tos_risk"),
            "audit_ref": a.get("audit_ref"),
        } for a in assessed]
        errors = client.insert_rows_json(table_id, rows)
        if errors:
            log.warning("BigQuery insert had errors: %s", errors)
            return 0
        return len(rows)
    except Exception as e:  # never let history break the run
        log.warning("BigQuery sink failed (non-fatal): %s", e)
        return 0
