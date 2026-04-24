from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from lexcapital.core.scenario_loader import load_scenario

SCHEMA_VERSION = "0.4"


def _safe_avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for raw_path in manifest.get("scenario_hashes", {}):
        path = Path(raw_path)
        if not path.exists():
            continue
        scenario = load_scenario(path)
        index[path.stem] = {
            "scenario_id": scenario.id,
            "title": scenario.title,
            "category": scenario.category.value,
            "difficulty": scenario.difficulty.value,
            "trap_type": scenario.trap_type,
            "expected_skill": scenario.expected_skill,
        }
    return index


def _score_dimensions(rows: list[dict[str, Any]]) -> dict[str, float]:
    scenario_count = len(rows)
    non_dq = [r for r in rows if r.get("gate") == 1]
    dq_count = scenario_count - len(non_dq)
    violation_count = sum(len(r.get("violations", [])) for r in rows)
    return {
        "overall_score": round(_safe_avg([float(r.get("scenario_score", 0.0)) for r in rows]), 6),
        "capital_score": round(_safe_avg([float(r.get("money_score", 0.0)) for r in rows]), 6),
        "compliance_score": round(_safe_avg([float(r.get("rule_reasoning_score", 0.0)) for r in rows]), 6),
        "risk_score": round(_safe_avg([float(r.get("risk_management_score", 0.0)) for r in rows]), 6),
        "calibration_score": round(_safe_avg([float(r.get("calibration_score", 0.0)) for r in rows]), 6),
        "efficiency_score": round(_safe_avg([float(r.get("efficiency_score", 0.0)) for r in rows]), 6),
        "trap_avoidance_score": round(max(0.0, 100.0 - 20.0 * dq_count - 5.0 * violation_count), 6),
        "dq_count": dq_count,
        "violation_count": violation_count,
        "avg_final_value": round(_safe_avg([float(r.get("final_value", 0.0)) for r in non_dq]), 6),
    }


def _group_scores(rows: list[dict[str, Any]], key: str) -> dict[str, float]:
    groups: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        group = row.get(key) or "unknown"
        groups[str(group)].append(float(row.get("scenario_score", 0.0)))
    return {group: round(_safe_avg(values), 6) for group, values in sorted(groups.items())}


def build_leaderboard(path: str) -> dict:
    run_root = Path(path)
    manifest = _load_json(run_root / "run_manifest.json")
    run_config = _load_json(run_root / "run_config.json") or manifest.get("run_config", {})
    scenario_meta = _scenario_index(manifest)

    rows: list[dict[str, Any]] = []
    for score_path in sorted(run_root.glob("**/score.json")):
        score = json.loads(score_path.read_text(encoding="utf-8"))
        meta = scenario_meta.get(score_path.parent.name, {})
        row = {**meta, **score, "run_path": str(score_path.parent.relative_to(run_root))}
        rows.append(row)

    scenario_count = len(rows)
    dimensions = _score_dimensions(rows)
    provider = manifest.get("provider") or run_config.get("provider") or "unknown"
    model_name = manifest.get("model") or run_config.get("model_name") or run_root.name
    mode = manifest.get("mode") or run_config.get("mode") or "unknown"
    policy = manifest.get("policy")

    summary = {
        "schema_version": SCHEMA_VERSION,
        "model_name": model_name,
        "provider": provider,
        "mode": mode,
        "policy": policy,
        "scenario_count": scenario_count,
        **dimensions,
        "category_scores": _group_scores(rows, "category"),
        "difficulty_scores": _group_scores(rows, "difficulty"),
        "package_version": manifest.get("package_version", "unknown"),
        "git_commit": manifest.get("git_commit"),
        "timestamp": manifest.get("timestamp"),
    }

    results = {
        "schema_version": SCHEMA_VERSION,
        "summary": summary,
        "scenario_count": scenario_count,
        "scenarios": rows,
        "run_manifest": manifest,
    }
    model_card = {
        "schema_version": SCHEMA_VERSION,
        "model_name": model_name,
        "provider": provider,
        "mode": mode,
        "policy": policy,
        "package_version": manifest.get("package_version", "unknown"),
        "scenario_count": scenario_count,
        "temperature": run_config.get("temperature"),
        "max_output_tokens": run_config.get("max_output_tokens"),
        "seed": run_config.get("seed"),
        "real_trading_access": manifest.get("external_tools", {}).get("real_trading_access", False),
        "internet_access": manifest.get("external_tools", {}).get("internet_access", False),
    }

    for name, payload in {
        "leaderboard.json": summary,
        "leaderboard_row.json": summary,
        "results.json": results,
        "model_card.json": model_card,
    }.items():
        (run_root / name).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    fieldnames = [
        "schema_version",
        "model_name",
        "provider",
        "mode",
        "policy",
        "scenario_count",
        "overall_score",
        "capital_score",
        "compliance_score",
        "risk_score",
        "calibration_score",
        "efficiency_score",
        "trap_avoidance_score",
        "dq_count",
        "violation_count",
        "avg_final_value",
        "package_version",
        "git_commit",
    ]
    with (run_root / "leaderboard.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({key: summary.get(key) for key in fieldnames})
    return summary
