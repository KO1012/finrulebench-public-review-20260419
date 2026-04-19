# FinRuleBench

FinRuleBench is a sandboxed financial reasoning benchmark for AI models.

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
python -m finrulebench validate scenarios/mvp
python -m finrulebench render-prompt --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml --step 0
python -m finrulebench run-suite --scenarios scenarios/mvp --adapter mock --model mock-hold --out runs/mock_hold
python -m finrulebench score-dir runs/mock_hold
pytest -q
```

## What it evaluates

- financial rule reading
- legal-style compliance boundaries
- synthetic market traps
- risk control
- calibration under uncertainty

## Safety boundary

FinRuleBench does **not** connect to real broker APIs, exchanges, wallets, or live trading systems.

## Core commands

- `python -m finrulebench validate scenarios/mvp`
- `python -m finrulebench render-prompt --scenario ... --step 0`
- `python -m finrulebench render-next --scenario ... --actions ...`
- `python -m finrulebench make-hold-actions --scenario ... --out /tmp/hold.jsonl`
- `python -m finrulebench replay --scenario ... --actions ... --out runs/example`
- `python -m finrulebench run-suite --scenarios scenarios/mvp --adapter mock --model mock-hold --out runs/mock_hold`
- `python -m finrulebench score-dir runs/mock_hold`
- `python -m finrulebench write-agent-template --out agent_eval.example.yaml`
- `python -m finrulebench agent-eval --config agent_eval.example.yaml`
- `python -m finrulebench self-eval`

## Agent integration

There are now two supported workflows for external coding agents.

### 1) API-backed model evaluation

Use this when the repository should call a configured provider adapter such as OpenAI or a local OpenAI-compatible endpoint.

```bash
python -m finrulebench self-eval \
  --adapter openai \
  --model gpt-5.4 \
  --scenarios scenarios/mvp \
  --out runs/gpt_5_4_self_eval
```

If your environment already exports `FINRULEBENCH_AGENT_ADAPTER` and `FINRULEBENCH_AGENT_MODEL`, the coding agent can often just run:

```bash
python -m finrulebench self-eval
```

### 2) Current coding agent self-evaluation

Use this when the external coding agent itself is the model being tested and the repository should **not** call a provider API.

The loop is:

1. Create an empty actions file for a scenario.
2. Ask for the next visible prompt:

```bash
python -m finrulebench render-next \
  --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml \
  --actions runs/self_eval/NOCTX-001/actions.jsonl
```

3. Append exactly one `ModelDecision` JSON line for the returned `next_step` using the agent's own reasoning.
4. Repeat `render-next` until it returns `{"done": true, ...}`.
5. Score the scenario:

```bash
python -m finrulebench replay \
  --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml \
  --actions runs/self_eval/NOCTX-001/actions.jsonl \
  --out runs/self_eval/NOCTX-001
```

6. Aggregate all scenario scores with:

```bash
python -m finrulebench score-dir runs/self_eval
```

This makes the repository usable even when the coding agent cannot expose its current model/provider to the benchmark code directly.

## Scoring

Adjusted utility uses final value, max drawdown, turnover, and invalid actions. Hard DQ sets scenario score to zero.

## Hidden-field defense

Prompt rendering uses an explicit allowlist. Hidden oracle text, trap conditions, hidden future data, and scoring config stay out of model prompts and run logs.

## Adding scenarios

Write YAML under `scenarios/mvp/` using the schema in `src/finrulebench/core/models.py`, then run:

```bash
python -m finrulebench validate scenarios/mvp
pytest -q
```
