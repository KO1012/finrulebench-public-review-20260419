from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class AgentEvalConfig(BaseModel):
    adapter: str = "openai"
    model: str
    mode: Literal["policy", "agent"] = "agent"
    scenarios: str = "scenarios/mvp"
    out: str = "runs/agent_eval"
    file_path: str | None = None
    base_url: str | None = None
    temperature: float = 0.0
    max_output_tokens: int = 1200
    timeout_seconds: int = 60
    max_retries: int = 1
    label: str | None = None
    notes: str | None = None


def load_agent_eval_config(path: str | Path) -> AgentEvalConfig:
    config_path = Path(path)
    suffix = config_path.suffix.lower()
    raw_text = config_path.read_text(encoding="utf-8")
    if suffix in {".yaml", ".yml"}:
        payload = yaml.safe_load(raw_text) or {}
    elif suffix == ".json":
        payload = json.loads(raw_text)
    else:
        raise ValueError("Agent eval config must be .yaml, .yml, or .json")
    return AgentEvalConfig.model_validate(payload)


def write_agent_eval_template(path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    template = AgentEvalConfig(
        adapter="openai",
        model="gpt-5.4",
        mode="agent",
        scenarios="scenarios/mvp",
        out="runs/gpt_5_4_agent",
        temperature=0.0,
        max_output_tokens=1200,
        timeout_seconds=60,
        max_retries=1,
        notes="Edit adapter/model/scenarios/out before running.",
    )
    out_path.write_text(yaml.safe_dump(template.model_dump(), sort_keys=False), encoding="utf-8")
    return out_path


def save_agent_eval_request(config: AgentEvalConfig, out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    request_path = out / "agent_eval_request.json"
    request_path.write_text(json.dumps(config.model_dump(), indent=2), encoding="utf-8")
    return request_path
