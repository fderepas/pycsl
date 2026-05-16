#!/usr/bin/env python3
"""
Agent Meta Monitor — operational watchdog for the self-healing agentic pipeline.

Parses captured logs from agent-reconcile.py and agent-script-update.py to compute
operational health metrics: JSON validation failures, MCP write rejections, and
total execution time derived from ISO-8601 timestamps in log lines.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

AGENT_NAME = "agent-meta-monitor"

try:
    from llm_client import log as _llm_log

    def log(msg: str, out_dir: Path) -> None:
        _llm_log(out_dir, AGENT_NAME, f"[{AGENT_NAME}] {msg}\n")
except ImportError:
    def log(msg: str, out_dir: Path) -> None:  # type: ignore[misc]
        print(f"[{AGENT_NAME}] {msg}")


REQUIRED_RECONCILE_KEYS = {"language", "author", "recommendation", "target"}

# Matches ISO-8601 timestamps written by llm_client.log(), e.g. [2026-05-10T22:33:20]
TS_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})")

# Matches MCP write-rejection log lines produced by agent-script-update-mcp.py
MCP_REJECT_PATTERN = re.compile(
    r"not in ALLOWED_TARGETS|tests/annotated/|forbidden path|write to forbidden|MCP.*reject",
    re.IGNORECASE,
)


def read_log(path: Path, out_dir: Path) -> list[str]:
    if not path.exists():
        log(f"Warning: log file not found: {path}", out_dir)
        return []
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        log(f"Warning: could not read {path}: {e}", out_dir)
        return []


def count_json_failures(reconcile_lines: list[str], out_dir: Path) -> int:
    """Count evidence of malformed or missing-key reconcile JSON in the log."""
    failures = 0
    combined = "\n".join(reconcile_lines)

    # Explicit parse-error log lines
    explicit = len(re.findall(
        r"Failed to parse (reconciliation )?JSON|JSONDecodeError",
        combined,
        re.IGNORECASE,
    ))
    failures += explicit

    # Embedded JSON blocks that look like partial reconcile output
    for block in re.findall(r"\{[^{}]+\}", combined):
        try:
            obj = json.loads(block)
            if isinstance(obj, dict) and obj:
                present = REQUIRED_RECONCILE_KEYS & set(obj.keys())
                missing = REQUIRED_RECONCILE_KEYS - set(obj.keys())
                if present and missing:
                    failures += 1
        except json.JSONDecodeError:
            pass

    return failures


def count_mcp_rejections(update_lines: list[str]) -> int:
    return sum(1 for line in update_lines if MCP_REJECT_PATTERN.search(line))


def compute_execution_time(all_lines: list[str]) -> Optional[float]:
    """Return elapsed seconds between first and last ISO timestamp, or None."""
    timestamps: list[datetime] = []
    for line in all_lines:
        m = TS_PATTERN.search(line)
        if m:
            try:
                timestamps.append(datetime.fromisoformat(m.group(1)))
            except ValueError:
                pass
    if len(timestamps) >= 2:
        return (timestamps[-1] - timestamps[0]).total_seconds()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Operational watchdog for the self-healing agentic pipeline"
    )
    parser.add_argument(
        "--reconcile-log",
        dest="reconcile_log",
        required=True,
        help="Path to the captured stdout/stderr log of agent-reconcile.py",
    )
    parser.add_argument(
        "--update-log",
        dest="update_log",
        required=True,
        help="Path to the captured stdout/stderr log of agent-script-update.py",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to the output JSON metrics file",
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_dir = out_path.parent

    reconcile_lines = read_log(Path(args.reconcile_log), out_dir)
    update_lines = read_log(Path(args.update_log), out_dir)

    json_failures = count_json_failures(reconcile_lines, out_dir)
    mcp_rejections = count_mcp_rejections(update_lines)
    exec_time = compute_execution_time(reconcile_lines + update_lines)
    health_status = "healthy" if (json_failures == 0 and mcp_rejections == 0) else "warning"

    log(
        f"json_validation_failures={json_failures}, mcp_rejection_count={mcp_rejections}, "
        f"total_execution_time_seconds={exec_time}, health_status={health_status}",
        out_dir,
    )

    result = {
        "json_validation_failures": json_failures,
        "mcp_rejection_count": mcp_rejections,
        "total_execution_time_seconds": exec_time,
        "health_status": health_status,
    }
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"Wrote monitor metrics to {out_path}", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
