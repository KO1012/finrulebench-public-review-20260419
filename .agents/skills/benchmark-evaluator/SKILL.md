---
name: benchmark-evaluator
description: Use this skill when you are asked to run lexcapital against a configured model or to evaluate the current coding agent.
---

When evaluating with this repository, prefer these workflows in order.

## Workflow A: self-eval

Use this when the repository can call a configured provider adapter or when the environment already exposes the current model/provider.

```bash
python -m lexcapital self-eval
```

If inference fails, pass explicit flags or set env vars:
- `LEXCAPITAL_AGENT_ADAPTER`
- `LEXCAPITAL_AGENT_MODEL`

Example:

```bash
python -m lexcapital self-eval --adapter openai --model gpt-5.4
```

## Workflow B: current coding agent self-evaluation

Use this when **you are the model being evaluated** and the repo should not call an external provider API.

For each scenario:

1. Start with an empty actions file.
2. Request the next visible prompt:

```bash
python -m lexcapital render-next --scenario <SCENARIO_YAML> --actions <ACTIONS_JSONL>
```

3. Append exactly one `ModelDecision` JSON line for the returned `next_step` using your own reasoning.
4. Repeat until `done=true`.
5. Score with:

```bash
python -m lexcapital replay --scenario <SCENARIO_YAML> --actions <ACTIONS_JSONL> --out <RUN_DIR>
```

6. Aggregate with:

```bash
python -m lexcapital score-dir <RUN_ROOT>
```

Hard rules:
- never connect to real trading systems
- never bypass prompt rendering
- never leak hidden oracle text, trap conditions, hidden future data, or scoring config
- keep all trading simulated
