from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lexcapital.core.audit import audit_scenarios


def publish_check(scenarios: str | Path, out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    audit_out = out_path / "scenario_audit"
    audit = audit_scenarios(scenarios, out=audit_out, run_replays=True)
    checks = {
        "validate_scenarios": audit["scenario_count"] > 0,
        "strict_hidden_leak_audit": audit["hidden_leakage_failures"] == 0,
        "hold_replay_non_dq": audit["hold_baseline_non_dq_rate"] == 1.0,
        "oracle_sidecars_non_dq": audit["oracle_paths_found"] == audit["scenario_count"]
        and audit.get("oracle_non_dq_rate") == 1.0,
        "red_sidecars_trigger_targets": audit["red_paths_found"] == audit["scenario_count"]
        and audit.get("red_path_trigger_rate") == 1.0,
        "metadata_coverage_complete": audit.get("metadata_complete_count") == audit["scenario_count"],
    }
    report = {
        "status": "pass" if all(checks.values()) and audit["status"] == "pass" else "fail",
        "checks": checks,
        "scenario_count": audit["scenario_count"],
        "metadata_complete_count": audit.get("metadata_complete_count", 0),
        "oracle_paths_found": audit["oracle_paths_found"],
        "red_paths_found": audit["red_paths_found"],
        "red_path_trigger_rate": audit["red_path_trigger_rate"],
        "category_balance": audit["category_balance"],
        "difficulty_balance": audit["difficulty_balance"],
        "audit_report_path": str(audit_out / "audit_report.json"),
        "failures": [entry for entry in audit["scenarios"] if entry["status"] != "pass"],
    }
    (out_path / "publish_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_path / "publish_summary.md").write_text(_summary_markdown(report), encoding="utf-8")
    return report


def _summary_markdown(report: dict[str, Any]) -> str:
    rows = ["# LexCapital publish check", "", f"Status: **{report['status']}**", "", "| Check | Pass |", "|---|---:|"]
    for key, value in report["checks"].items():
        rows.append(f"| `{key}` | `{value}` |")
    rows.extend([
        "",
        f"Scenarios: **{report['scenario_count']}**",
        f"Metadata complete: **{report['metadata_complete_count']}**",
        f"Oracle sidecars: **{report['oracle_paths_found']}**",
        f"Red sidecars: **{report['red_paths_found']}**",
        "",
    ])
    return "\n".join(rows)
