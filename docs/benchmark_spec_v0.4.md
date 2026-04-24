# lexcapital Benchmark Spec v0.4

v0.4 upgrades lexcapital from a publishable MVP into a leaderboard-ready financial reasoning benchmark.

## Scope

- All trading is simulated; there is no brokerage, exchange, wallet, or live trading integration.
- Hidden oracle solutions, trap conditions, hidden future fields, scoring configs, and author notes must never be rendered into model prompts.
- Every run must be reproducible from saved scenario YAML, actions JSONL, score JSON, and run manifests.

## Scenario pack

The v0.4 public pack keeps the audited 14-scenario MVP suite as the stable compatibility core and defines the expansion track for 30-50 scenarios across:

- stocks and event-driven situations
- funds and ETF creation/redemption mechanics
- rates and cash instruments
- rule-arbitrage mechanics
- prediction market resolution rules
- crypto/perp settlement and bridge timing
- options and margin traps
- regulation and information-boundary scenarios

## Required run artifacts

Every suite or baseline run should write:

- `run_manifest.json`
- `run_config.json`
- per-scenario `actions.jsonl`
- per-scenario `score.json`
- `leaderboard.json`
- `leaderboard_row.json`
- `leaderboard.csv`
- `results.json`
- `model_card.json`

## Leaderboard dimensions

v0.4 ranks models by:

- overall score
- capital score
- compliance score
- risk score
- calibration score
- efficiency score
- trap-avoidance score
- category-level scores
- difficulty-level scores

## Baselines

Required public baselines:

- `hold`
- `random-valid`
- `rule-aware`
- `risk-aware`
- `oracle-lite`

`oracle-lite` replays public oracle sidecars when available. It is a calibration ceiling, not a hidden test oracle.

## Release gate

Before publishing:

```bash
python -m lexcapital validate scenarios/mvp
python -m lexcapital audit-scenarios --scenarios scenarios/mvp --strict
python -m lexcapital publish-check --scenarios scenarios/mvp --out audits/publish_mvp_v0.4
pytest -q
```
