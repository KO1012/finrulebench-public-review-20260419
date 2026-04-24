# lexcapital

lexcapital is a sandboxed financial reasoning benchmark for AI models.

## Principles

- Every scenario starts with **100 USD**.
- All trading is simulated.
- Hidden fields never reach the evaluated model.
- Deterministic replay produces the final score.
- HOLD is always valid.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Minimal demo

```bash
python -m lexcapital validate scenarios/mvp
python -m lexcapital render-prompt --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml --step 0
python -m lexcapital run-suite --scenarios scenarios/mvp --adapter mock --model mock-hold --out runs/mock_hold
python -m lexcapital run-baseline --policy rule-aware --scenarios scenarios/mvp --out runs/baselines/rule_aware
python -m lexcapital run-baseline --policy risk-aware --scenarios scenarios/mvp --out runs/baselines/risk_aware
python -m lexcapital run-baseline --policy oracle-lite --scenarios scenarios/mvp --out runs/baselines/oracle_lite
python -m lexcapital publish-check --scenarios scenarios/mvp --out audits/publish_mvp
python -m lexcapital score-dir runs/mock_hold
pytest -q
```

## What it evaluates

- financial rule reading
- legal-style compliance boundaries
- synthetic market traps
- risk control
- calibration under uncertainty

## Safety boundary

lexcapital does **not** connect to real broker APIs, exchanges, wallets, or live trading systems.

## Core commands

- `python -m lexcapital validate scenarios/mvp`
- `python -m lexcapital render-prompt --scenario ... --step 0`
- `python -m lexcapital render-next --scenario ... --actions ...`
- `python -m lexcapital make-hold-actions --scenario ... --out /tmp/hold.jsonl`
- `python -m lexcapital replay --scenario ... --actions ... --out runs/example`
- `python -m lexcapital run-suite --scenarios scenarios/mvp --adapter mock --model mock-hold --out runs/mock_hold`
- `python -m lexcapital run-baseline --policy hold --scenarios scenarios/mvp --out runs/baselines/hold`
- `python -m lexcapital run-baseline --policy random-valid --seed 42 --scenarios scenarios/mvp --out runs/baselines/random_valid`
- `python -m lexcapital run-baseline --policy rule-aware --scenarios scenarios/mvp --out runs/baselines/rule_aware`
- `python -m lexcapital run-baseline --policy risk-aware --scenarios scenarios/mvp --out runs/baselines/risk_aware`
- `python -m lexcapital run-baseline --policy oracle-lite --scenarios scenarios/mvp --out runs/baselines/oracle_lite`
- `python -m lexcapital publish-check --scenarios scenarios/mvp --out audits/publish_mvp`
- `python -m lexcapital score-dir runs/mock_hold`
- `python -m lexcapital write-agent-template --out agent_eval.example.yaml`
- `python -m lexcapital agent-eval --config agent_eval.example.yaml`
- `python -m lexcapital self-eval`
- `python -m lexcapital audit-scenarios --scenarios scenarios/mvp --out audits/mvp`

## Agent integration

There are now two supported workflows for external coding agents.

### 1) API-backed model evaluation

Use this when the repository should call a configured provider adapter such as OpenAI or a local OpenAI-compatible endpoint.

```bash
python -m lexcapital self-eval \
  --adapter openai \
  --model gpt-5.4 \
  --scenarios scenarios/mvp \
  --out runs/gpt_5_4_self_eval
```

If your environment already exports `LEXCAPITAL_AGENT_ADAPTER` and `LEXCAPITAL_AGENT_MODEL`, the coding agent can often just run:

```bash
python -m lexcapital self-eval
```

### 2) Current coding agent self-evaluation

Use this when the external coding agent itself is the model being tested and the repository should **not** call a provider API.

The loop is:

1. Create an empty actions file for a scenario.
2. Ask for the next visible prompt:

```bash
python -m lexcapital render-next \
  --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml \
  --actions runs/self_eval/NOCTX-001/actions.jsonl
```

3. Append exactly one `ModelDecision` JSON line for the returned `next_step` using the agent's own reasoning.
4. Repeat `render-next` until it returns `{"done": true, ...}`.
5. Score the scenario:

```bash
python -m lexcapital replay \
  --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml \
  --actions runs/self_eval/NOCTX-001/actions.jsonl \
  --out runs/self_eval/NOCTX-001
```

6. Aggregate all scenario scores with:

```bash
python -m lexcapital score-dir runs/self_eval
```

This makes the repository usable even when the coding agent cannot expose its current model/provider to the benchmark code directly.

## Scoring

Adjusted utility uses final value, max drawdown, turnover, and invalid actions. Hard DQ sets scenario score to zero.

## Hidden-field defense

Prompt rendering uses an explicit allowlist. Hidden oracle text, trap conditions, hidden future data, and scoring config stay out of model prompts and run logs.

## Adding scenarios

Write YAML under `scenarios/mvp/` using the schema in `src/lexcapital/core/models.py`, then run:

```bash
python -m lexcapital validate scenarios/mvp
pytest -q
```


## v0.4 leaderboard protocol

v0.4 writes leaderboard-ready artifacts for every suite or baseline run:

- `results.json`: full machine-readable run output with per-scenario scores
- `model_card.json`: provider/model/config/access boundary metadata
- `leaderboard_row.json`: one normalized leaderboard submission row
- `leaderboard.csv`: flat CSV row for aggregation

The public baselines are `hold`, `random-valid`, `rule-aware`, `risk-aware`, and `oracle-lite`.

## v0.3 scenario audit and publish gate

Use the audit and publish-check commands before expanding the benchmark or publishing a run:

```bash
python -m lexcapital audit-scenarios --scenarios scenarios/mvp --out audits/mvp_v0.3 --strict
python -m lexcapital publish-check --scenarios scenarios/mvp --out audits/publish_mvp_v0.3
```

The audit checks hidden-field leakage, HOLD replay safety, oracle/red sidecars, metadata coverage, provenance coverage, and category/difficulty/trap balance. It writes `audit_report.json` and `audit_summary.md`; publish-check writes `publish_report.json` and `publish_summary.md`.

## v0.4 docs

- `docs/benchmark_spec_v0.4.md`
- `docs/leaderboard_schema_v0.4.md`
- `docs/v0.4_release_notes.md`
- `docs/scenario_authoring_guide.md`
- `docs/eval_protocol.md`
- `docs/scoring_rubric.md`
