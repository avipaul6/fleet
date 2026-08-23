# DuckFleet household profile — the `profile.json` contract

This is the file the DuckFleet fleet reads at startup ([config/settings.py](../../config/settings.py))
and overlays on top of its defaults. Every field is optional; omit what you don't know and
the fleet fills a sensible default. Produce **valid JSON only** — no comments, no trailing commas.

## Fields

| Field | Type | Notes |
|---|---|---|
| `programs` | array of strings | Loyalty programs the user collects. |
| `prefs_avoid` | array of strings | Categories to **never** surface. |
| `prefs_conditional` | object (string → number) | Category → minimum net AUD to surface it. Show these only if a deal clears the threshold. |
| `spend_cap_aud_per_week` | number or null | Weekly spend the fleet may assume. Default 100. |
| `time_value_aud_per_hour` | number or null | Used in "is this errand worth it?" maths. Usually left null. |
| `notify_email` | string or null | Where the morning brief is emailed. |
| `home_label` | string or null | Suburb and/or postcode (drive-worth judgement). |

### Allowed values (enums — use these EXACTLY, nothing else)

- `programs` items: `qantas_ff`, `velocity`, `flybuys`, `everyday_rewards`
- `prefs_avoid` items **and** `prefs_conditional` keys: `credit_card`, `insurance`,
  `energy`, `telco`, `groceries`, `subscription`, `collectible`, `shopping`, `other`

## Example

```json
{
  "programs": ["qantas_ff", "flybuys"],
  "prefs_avoid": ["credit_card"],
  "prefs_conditional": { "insurance": 300 },
  "spend_cap_aud_per_week": 100,
  "notify_email": "me@example.com",
  "home_label": "Bondi NSW 2026"
}
```

## Formal JSON Schema

```json
{
  "title": "Profile",
  "type": "object",
  "properties": {
    "programs": {
      "type": "array",
      "items": { "enum": ["qantas_ff", "velocity", "flybuys", "everyday_rewards"], "type": "string" },
      "default": []
    },
    "prefs_avoid": {
      "type": "array",
      "items": { "enum": ["credit_card", "insurance", "energy", "telco", "groceries", "subscription", "collectible", "shopping", "other"], "type": "string" },
      "default": []
    },
    "prefs_conditional": {
      "type": "object",
      "additionalProperties": { "type": "number" },
      "default": {}
    },
    "spend_cap_aud_per_week": { "anyOf": [{ "type": "number" }, { "type": "null" }], "default": null },
    "time_value_aud_per_hour": { "anyOf": [{ "type": "number" }, { "type": "null" }], "default": null },
    "notify_email": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
    "home_label": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null }
  }
}
```
