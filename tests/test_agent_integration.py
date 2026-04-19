from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from finrulebench.agent_integration import (
    AgentEvalConfig,
    load_agent_eval_config,
    save_agent_eval_request,
    write_agent_eval_template,
)
from finrulebench.cli import app


runner = CliRunner()


def test_write_and_load_agent_eval_template(tmp_path: Path):
    config_path = tmp_path / "agent_eval.yaml"
    write_agent_eval_template(config_path)
    cfg = load_agent_eval_config(config_path)
    assert cfg.adapter == "openai"
    assert cfg.mode == "agent"
    assert cfg.model


def test_save_agent_eval_request(tmp_path: Path):
    cfg = AgentEvalConfig(model="mock-hold", adapter="mock", out=str(tmp_path / "runs"))
    request_path = save_agent_eval_request(cfg, cfg.out)
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    assert payload["model"] == "mock-hold"
    assert payload["adapter"] == "mock"


def test_agent_eval_cli_writes_request_and_prints_summary(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "agent_eval.yaml"
    config_payload = {
        "adapter": "mock",
        "model": "mock-hold",
        "mode": "agent",
        "scenarios": "scenarios/mvp",
        "out": str(tmp_path / "runs"),
    }
    config_path.write_text(yaml.safe_dump(config_payload, sort_keys=False), encoding="utf-8")

    def fake_run_suite(scenarios, adapter_obj, run_config, out):
        out_path = Path(out)
        out_path.mkdir(parents=True, exist_ok=True)
        (out_path / "suite_summary.json").write_text(json.dumps({"overall_score": 12.34}), encoding="utf-8")

    monkeypatch.setattr("finrulebench.cli.run_suite_impl", fake_run_suite)
    monkeypatch.setattr("finrulebench.cli.build_leaderboard", lambda path: {"overall_score": 12.34})

    result = runner.invoke(app, ["agent-eval", "--config", str(config_path)])
    assert result.exit_code == 0
    assert "12.34" in result.stdout
    assert (tmp_path / "runs" / "agent_eval_request.json").exists()
