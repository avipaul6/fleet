-- DuckFleet — ROI from BigQuery (the "does the run earn its compute?" beat).
--
-- Value side is REAL, straight from offer_history: it mirrors economics.py exactly —
--   value = SUM(net_value_aud) WHERE verdict IN ('do_it','needs_approval').
-- Compute side is NOT stored per row (it's runtime token/API accounting in economics.py),
-- so we DECLARE it as the same order-of-magnitude estimate the email uses. Per economics.py:
-- "Prices are ORDER-OF-MAGNITUDE estimates ... the point is the ratio, not penny precision."
--
-- Run:  bq query --use_legacy_sql=false < demo/gcp-hackathon/roi.sql

DECLARE compute_aud_per_run FLOAT64 DEFAULT 0.003;  -- ~one replay run (Gemini-flash tokens); tune to billing

WITH per_run AS (
  SELECT
    run_ts,
    mode,
    ROUND(SUM(IF(verdict IN ('do_it','needs_approval'), net_value_aud, 0)), 2) AS value_aud,
    COUNTIF(verdict IN ('do_it','needs_approval'))                             AS acted,
    COUNTIF(verdict = 'skip')                                                  AS skipped
  FROM `duckfleet-agents.duckfleet.offer_history`
  GROUP BY run_ts, mode
)
SELECT
  FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', run_ts) AS run,
  mode,
  acted,
  skipped,
  compute_aud_per_run AS compute_aud,
  value_aud,
  CAST(ROUND(SAFE_DIVIDE(value_aud, compute_aud_per_run)) AS INT64) AS roi_x,
  -- the exact email-style line:
  FORMAT('🧮 ~$%.3f compute → $%.2f value (≈%d× return)',
         compute_aud_per_run,
         value_aud,
         CAST(ROUND(SAFE_DIVIDE(value_aud, compute_aud_per_run)) AS INT64)) AS roi_line
FROM per_run
ORDER BY run_ts DESC;
