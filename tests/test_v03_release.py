import json
import subprocess
import sys
from pathlib import Path

from lexcapital.core.audit import audit_scenarios

from .conftest import ROOT


def run_cli(*args, tmp_path=None):
    return subprocess.run(
        [sys.executable, "-m", "lexcapital", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_v03_package_version_is_coherent():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.3.0"' in pyproject
    assert (ROOT / "docs" / "benchmark_spec_v0.3.md").exists()


def test_mvp_pack_has_complete_v03_metadata_and_sidecars():
    report = audit_scenarios(ROOT / "scenarios" / "mvp", run_replays=True)
    assert report["scenario_count"] == 14
    assert report["metadata_complete_count"] == 14
    assert report["oracle_paths_found"] == 14
    assert report["red_paths_found"] == 14
    assert report["red_path_trigger_rate"] == 1.0


def test_run_baseline_cli_writes_replayable_results(tmp_path):
    out = tmp_path / "baseline_hold"
    result = run_cli(
        "run-baseline",
        "--policy",
        "hold",
        "--scenarios",
        "scenarios/mvp",
        "--out",
        str(out),
    )
    assert result.returncode == 0, result.stderr
    assert (out / "run_manifest.json").exists()
    summary = json.loads((out / "suite_summary.json").read_text(encoding="utf-8"))
    assert summary["scenario_count"] == 14


def test_publish_check_cli_passes_for_mvp(tmp_path):
    out = tmp_path / "publish"
    result = run_cli("publish-check", "--scenarios", "scenarios/mvp", "--out", str(out))
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((out / "publish_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "pass"
    assert report["metadata_complete_count"] == 14
    assert report["oracle_paths_found"] == 14
    assert report["red_paths_found"] == 14


def test_run_suite_writes_reproducible_manifest(tmp_path):
    out = tmp_path / "suite"
    result = run_cli(
        "run-suite",
        "--scenarios",
        "scenarios/mvp",
        "--adapter",
        "mock",
        "--model",
        "mock-hold",
        "--out",
        str(out),
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["package_version"] == "0.3.0"
    assert manifest["scenario_count"] == 14
    assert manifest["scenario_hashes"]
    assert manifest["run_config"]["model_name"] == "mock-hold"
