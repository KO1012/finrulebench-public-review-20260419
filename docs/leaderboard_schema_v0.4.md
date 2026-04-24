# v0.4 Leaderboard Schema

`leaderboard_row.json` and each row in `leaderboard.csv` represent one model run.

## Required fields

- `schema_version`: currently `0.4`
- `model_name`
- `provider`
- `mode`: `policy` or `agent`
- `policy`: baseline policy name, if applicable
- `scenario_count`
- `overall_score`
- `capital_score`
- `compliance_score`
- `risk_score`
- `calibration_score`
- `efficiency_score`
- `trap_avoidance_score`
- `dq_count`
- `violation_count`
- `avg_final_value`
- `category_scores`
- `difficulty_scores`
- `package_version`
- `git_commit`
- `timestamp`

## `results.json`

`results.json` is the full machine-readable artifact:

```json
{
  "schema_version": "0.4",
  "summary": {},
  "scenario_count": 14,
  "scenarios": [],
  "run_manifest": {}
}
```

## `model_card.json`

`model_card.json` records provider/model identity and access boundaries. `real_trading_access` must always be `false`.
