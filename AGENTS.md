# FinRuleBench Agent Instructions

## Project purpose

FinRuleBench is a sandboxed AI financial decision benchmark. It evaluates models on simulated trading scenarios with legal-style rules, hidden traps, risk constraints, and deterministic scoring.

## Non-negotiable safety rules

- Never connect to real brokerages, real exchanges, wallets, or live trading APIs.
- Never implement real-world market manipulation, wash trading, spoofing, illegal arbitrage, or regulatory evasion.
- All trading must be simulated.
- Rule loopholes are synthetic scenario mechanics only.
- Never expose hidden_oracle_solution, trap_conditions, hidden_future, scoring, or notes_for_authors to model prompts.
- Do not require or reveal chain-of-thought. Use short rationale summaries only.
- Do not use Python eval or exec on scenario YAML fields.

## Engineering rules

- Use Python 3.11+.
- Use pydantic v2 for schemas.
- Every scenario must have deterministic validation, replay, and scoring.
- Every scenario starts with 100 USD.
- HOLD must be a valid action.
- Replay is deterministic and based on saved actions.jsonl.
- The model runner collects actions; the replay engine scores them.
- Private hidden fields must never be sent to adapters or agents.

## External coding-agent workflow

When a coding agent enters this repository and is asked to benchmark itself or another configured model, prefer these workflows in order.

### Workflow A: self-eval

Use this when the repository can call a configured provider adapter or when the environment already exposes the current model/provider.

```bash
python -m finrulebench self-eval
```

If automatic inference fails, pass explicit flags or set env vars:

- `FINRULEBENCH_AGENT_ADAPTER`
- `FINRULEBENCH_AGENT_MODEL`

Example:

```bash
python -m finrulebench self-eval --adapter openai --model gpt-5.4
```

### Workflow B: current coding agent self-evaluation loop

Use this when **you are the model being evaluated** and the repo should not call a provider API directly.

For each scenario:

1. Create an empty actions file.
2. Request the next visible prompt:

```bash
python -m finrulebench render-next --scenario <SCENARIO_YAML> --actions <ACTIONS_JSONL>
```

3. Append exactly one `ModelDecision` JSON line for the returned `next_step`, using your own reasoning.
4. Repeat `render-next` until `done=true`.
5. Score the scenario:

```bash
python -m finrulebench replay --scenario <SCENARIO_YAML> --actions <ACTIONS_JSONL> --out <RUN_DIR>
```

6. Aggregate results:

```bash
python -m finrulebench score-dir <RUN_ROOT>
```

Hard rule: do not bypass prompt rendering by reading hidden fields directly.

## Required verification commands

```bash
python -m finrulebench validate scenarios/mvp
python -m finrulebench render-prompt --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml --step 0
python -m finrulebench render-next --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml --actions /tmp/noctx_actions.jsonl
python -m finrulebench make-hold-actions --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml --out /tmp/noctx_hold.jsonl
python -m finrulebench replay --scenario scenarios/mvp/noctx_001_no_edge_hold.yaml --actions /tmp/noctx_hold.jsonl --out runs/noctx_hold
python -m finrulebench self-eval --adapter mock --model mock-hold --scenarios scenarios/mvp --out runs/mock_self_eval
pytest -q
```

## Definition of done

A change is done only when:

- all relevant tests pass
- CLI commands run successfully
- hidden fields are not leaked
- no real trading integration exists
- README explains the new behavior
