import json
import subprocess
import sys
from pathlib import Path

from .conftest import ROOT


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "lexcapital", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_v04_package_version_and_docs_exist():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.4.0"' in pyproject
    assert (ROOT / "docs" / "benchmark_spec_v0.4.md").exists()
    assert (ROOT / "docs" / "v0.4_release_notes.md").exists()
    assert (ROOT / "docs" / "leaderboard_schema_v0.4.md").exists()


def test_v04_baseline_policies_run_and_write_leaderboard_artifacts(tmp_path):
    for policy in ["risk-aware", "oracle-lite"]:
        out = tmp_path / policy
        result = run_cli(
            "run-baseline",
            "--policy",
            policy,
            "--scenarios",
            "scenarios/mvp",
            "--out",
            str(out),
            "--seed",
            "42",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        summary = json.loads((out / "suite_summary.json").read_text(encoding="utf-8"))
        assert summary["policy"] == policy
        assert summary["scenario_count"] == 14
        for artifact in ["leaderboard.json", "leaderboard.csv", "leaderboard_row.json", "results.json", "model_card.json"]:
            assert (out / artifact).exists(), artifact
        row = json.loads((out / "leaderboard_row.json").read_text(encoding="utf-8"))
        assert row["schema_version"] == "0.4"
        assert "calibration_score" in row
        assert "trap_avoidance_score" in row
        assert "category_scores" in row
        assert "difficulty_scores" in row


def test_score_dir_writes_v04_results_and_model_card(tmp_path):
    out = tmp_path / "hold"
    result = run_cli(
        "run-baseline",
        "--policy",
        "hold",
        "--scenarios",
        "scenarios/mvp",
        "--out",
        str(out),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    score_result = run_cli("score-dir", str(out))
    assert score_result.returncode == 0, score_result.stdout + score_result.stderr
    results = json.loads((out / "results.json").read_text(encoding="utf-8"))
    model_card = json.loads((out / "model_card.json").read_text(encoding="utf-8"))
    assert results["schema_version"] == "0.4"
    assert results["scenario_count"] == 14
    assert len(results["scenarios"]) == 14
    assert model_card["model_name"] == "baseline-hold"
    assert model_card["provider"] == "baseline"
    assert model_card["real_trading_access"] is False


def test_readme_advertises_v04_leaderboard_protocol():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "v0.4" in readme
    assert "results.json" in readme
    assert "risk-aware" in readme
    assert "oracle-lite" in readme
