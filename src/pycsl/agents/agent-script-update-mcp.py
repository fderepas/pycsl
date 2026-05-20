from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

SERVER_NAME = "PyCSL-Script-Update"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
mcp = FastMCP(SERVER_NAME)


ANNOTATED_DIR = (PROJECT_ROOT / "tests" / "annotated").resolve()


def _load_allowed_targets() -> set[Path]:
    default = {
        (PROJECT_ROOT / "src" / "pycsl" / "agents" / "agent-annotate.py").resolve(),
        (PROJECT_ROOT / "config" / "skills" / "pycsl-annotate" / "SKILL.md").resolve(),
    }
    config_path = PROJECT_ROOT / "config" / "agents-config.json"
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        extra = cfg.get("script-update-allowed-targets", [])
        return default | {(PROJECT_ROOT / p).resolve() for p in extra}
    except (FileNotFoundError, json.JSONDecodeError):
        return default


ALLOWED_TARGETS = _load_allowed_targets()


def _safe_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"path escapes PyCSL root: {path}") from exc
    # Block any write that would touch tests/annotated/
    try:
        candidate.relative_to(ANNOTATED_DIR)
        raise ValueError(f"writes to tests/annotated/ are forbidden: {path}")
    except ValueError as exc:
        if "forbidden" in str(exc):
            raise
    return candidate


def _json(ok: bool, **payload: Any) -> str:
    return json.dumps({"ok": ok, **payload}, ensure_ascii=False, indent=2)


def _list_targets() -> list[str]:
    """Return the fixed set of files that may be updated by this agent."""
    targets: list[str] = []
    for path in sorted(ALLOWED_TARGETS):
        if path.exists():
            targets.append(str(path.relative_to(PROJECT_ROOT)))
    return targets


@mcp.tool()
def list_update_targets() -> str:
    return _json(True, targets=_list_targets())


@mcp.tool()
def read_text_file(path: str) -> str:
    file_path = _safe_path(path)
    if not file_path.exists():
        return _json(False, error=f"file not found: {path}")
    if not file_path.is_file():
        return _json(False, error=f"not a file: {path}")
    return _json(True, path=str(file_path.relative_to(PROJECT_ROOT)), content=file_path.read_text(encoding="utf-8"))


@mcp.tool()
def read_json_file(path: str) -> str:
    file_path = _safe_path(path)
    if not file_path.exists():
        return _json(False, error=f"file not found: {path}")
    if not file_path.is_file():
        return _json(False, error=f"not a file: {path}")
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _json(False, error=f"invalid JSON in {path}: {exc}")
    return _json(True, path=str(file_path.relative_to(PROJECT_ROOT)), data=data)


@mcp.tool()
def write_text_file(path: str, content: str) -> str:
    file_path = _safe_path(path)
    if file_path not in ALLOWED_TARGETS:
        return _json(False, error=f"write rejected: {path} is not an allowed update target")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return _json(True, path=str(file_path.relative_to(PROJECT_ROOT)))


@mcp.tool()
def replace_text(path: str, old_text: str, new_text: str, count: int = 1) -> str:
    file_path = _safe_path(path)
    if file_path not in ALLOWED_TARGETS:
        return _json(False, error=f"write rejected: {path} is not an allowed update target")
    if not file_path.exists():
        return _json(False, error=f"file not found: {path}")
    if not file_path.is_file():
        return _json(False, error=f"not a file: {path}")

    original = file_path.read_text(encoding="utf-8")
    if old_text not in original:
        return _json(False, error=f"old text not found in {path}")

    updated = original.replace(old_text, new_text, count)
    file_path.write_text(updated, encoding="utf-8")
    return _json(True, path=str(file_path.relative_to(PROJECT_ROOT)))


if __name__ == "__main__":
    mcp.run()
