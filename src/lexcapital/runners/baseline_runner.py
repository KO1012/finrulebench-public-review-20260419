from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from lexcapital.core.leaderboard import build_leaderboard
from lexcapital.core.manifest import build_run_manifest, write_run_manifest
from lexcapital.core.models import ModelDecision, Scenario
from lexcapital.core.replay import replay_scenario
from lexcapital.core.scenario_loader import load_scenario
from lexcapital.policies.baseline_hold import make_hold_decisions
from lexcapital.policies.random_valid import make_random_valid_decisions
from lexcapital.policies.rule_aware_heuristic import make_rule_aware_decisions
from lexcapital.runners.run_config import RunConfig
from lexcapital.runners.suite_runner import iter_scenario_paths

PolicyFactory = Callable[[Scenario], list[ModelDecision]]


def _write_decisions(path: Path, decisions: list[ModelDecision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for decision in decisions:
            handle.write(json.dumps(decision.model_dump(mode="json"), sort_keys=True) + "\n")


def _factory(policy: str, seed: int | None = None) -> PolicyFactory:
    key = policy.lower().replace("_", "-")
    if key == "hold":
        return lambda scenario: make_hold_decisions(scenario.max_steps)
    if key == "random-valid":
        return lambda scenario: make_random_valid_decisions(scenario, seed=seed)
    if key == "rule-aware":
        return make_rule_aware_decisions
    raise ValueError(f"Unknown baseline policy: {policy}")


def run_baseline(policy: str, scenarios: str | Path, out: str | Path, seed: int | None = None) -> dict:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    factory = _factory(policy, seed=seed)
    run_config = RunConfig(
        model_name=f"baseline-{policy}",
        provider="baseline",
        mode="policy",
        seed=seed,
    )
    write_run_manifest(
        out_path,
        build_run_manifest(scenarios, run_config, mode="policy", policy=policy),
    )
    (out_path / "run_config.json").write_text(run_config.model_dump_json(indent=2), encoding="utf-8")
    for scenario_path in iter_scenario_paths(scenarios):
        scenario = load_scenario(scenario_path)
        scenario_out = out_path / scenario_path.stem
        scenario_out.mkdir(parents=True, exist_ok=True)
        actions_path = scenario_out / "actions.jsonl"
        _write_decisions(actions_path, factory(scenario))
        replay_scenario(str(scenario_path), str(actions_path), str(scenario_out))
    summary = build_leaderboard(str(out_path))
    summary.update({"provider": "baseline", "mode": "policy", "model_name": f"baseline-{policy}", "policy": policy})
    (out_path / "suite_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_path / "leaderboard_row.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
