from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from lexcapital.core.audit import iter_scenario_yaml_paths


def package_version() -> str:
    try:
        return version("lexcapital")
    except PackageNotFoundError:
        pyproject = Path("pyproject.toml")
        if pyproject.exists():
            for line in pyproject.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version ="):
                    return line.split("=", 1)[1].strip().strip('"')
        return "unknown"


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_run_manifest(
    scenarios_root: str | Path,
    run_config: Any,
    *,
    adapter: Any | None = None,
    mode: str | None = None,
    policy: str | None = None,
) -> dict[str, Any]:
    scenario_paths = iter_scenario_yaml_paths(scenarios_root)
    config_payload = run_config.model_dump(mode="json") if hasattr(run_config, "model_dump") else dict(run_config)
    return {
        "package_version": package_version(),
        "git_commit": git_commit(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_root": str(scenarios_root),
        "scenario_count": len(scenario_paths),
        "scenario_hashes": {str(path): file_sha256(path) for path in scenario_paths},
        "run_config": config_payload,
        "adapter": getattr(adapter, "name", None),
        "provider": getattr(adapter, "provider", config_payload.get("provider")),
        "model": config_payload.get("model_name"),
        "mode": mode or config_payload.get("mode"),
        "policy": policy,
        "external_tools": {
            "internet_access": False,
            "filesystem_access": False,
            "code_execution": False,
            "real_trading_access": False,
        },
    }


def write_run_manifest(out_dir: str | Path, manifest: dict[str, Any]) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "run_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path
