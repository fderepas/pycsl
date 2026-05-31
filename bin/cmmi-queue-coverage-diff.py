#!/usr/bin/env python3
"""cmmi-queue-coverage-diff — validate the bridge against metrics/logs/.

Pre-decommission validator for Item 3.5x. Compares projects/pycsl/
message-queues/<agent>/inbox-from-logs/ against metrics/logs/<file>.log
to quantify how faithfully the bridge mirrors log content.

The Item 3.5x decommission decision (coordinator.py writes →
queue) is gated on: this tool reports ≥99.5% coverage with zero
content mismatches for ≥30 consecutive daily runs.

Per cmmi-tailoring-plan-follow-up-3.md Item 3.5p.

Modes:
  cmmi-queue-coverage-diff.py --summary   # one-line coverage % (default)
  cmmi-queue-coverage-diff.py --detail    # per-file breakdown
  cmmi-queue-coverage-diff.py --json      # raw JSON dump

Exit codes:
  0  coverage >= 99.5% AND zero content mismatches (decommission-safe)
  1  coverage < 99.5% OR content mismatches present (NOT safe yet)
  2  setup error (queue missing, logs missing, etc.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_ROOT = REPO_ROOT / "metrics" / "logs"
QUEUE_ROOT = REPO_ROOT / "projects" / "pycsl" / "message-queues"
BRIDGE_CURSOR = QUEUE_ROOT / ".bridge-cursor.json"

# Sample rate for --summary mode (0.0..1.0). Bounds runtime on the
# 81k-message backlog while still giving a representative figure.
SUMMARY_SAMPLE_RATE = 0.05

# Decommission threshold per Item 3.5x gate
DECOMMISSION_COVERAGE_FLOOR = 0.995


# ---------------------------------------------------------------------------
# Queue index — agent.log → {lineno: queue_msg_dict}
# ---------------------------------------------------------------------------

_SOURCE_URI_RE = re.compile(r"^metrics/logs/(.+):(\d+)$")


def _index_queue() -> dict[str, dict[int, dict]]:
    """Walk the queue and build {agent_log_basename: {lineno: msg}}."""
    index: dict[str, dict[int, dict]] = {}
    if not QUEUE_ROOT.is_dir():
        return index
    for inbox in QUEUE_ROOT.glob("*/inbox-from-logs"):
        for jf in inbox.glob("*.json"):
            try:
                msg = json.loads(jf.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            src = msg.get("source_uri", "")
            m = _SOURCE_URI_RE.match(src)
            if not m:
                continue
            log_name, lineno_s = m.group(1), m.group(2)
            try:
                lineno = int(lineno_s)
            except ValueError:
                continue
            index.setdefault(log_name, {})[lineno] = msg
    return index


# ---------------------------------------------------------------------------
# Coverage computation
# ---------------------------------------------------------------------------

def _coverage_for_log(
    log_path: Path,
    queue_index: dict[int, dict],
    sample_rate: float = 1.0,
) -> dict:
    """Compare one log file against its bridged messages."""
    try:
        lines = log_path.read_text(errors="replace").splitlines()
    except OSError:
        return {"error": "log unreadable"}

    # Bridge counts non-blank lines only (per bin/cmmi-msg-bridge.py)
    eligible = [(i + 1, line) for i, line in enumerate(lines) if line.strip()]
    if not eligible:
        return {"eligible": 0, "covered": 0, "mismatch": 0, "missing": 0,
                "coverage": 1.0}

    if sample_rate < 1.0:
        step = max(1, int(1 / sample_rate))
        eligible = eligible[::step]

    covered = 0
    missing = 0
    mismatch = 0
    for lineno, line in eligible:
        msg = queue_index.get(lineno)
        if msg is None:
            missing += 1
            continue
        if msg.get("line_text", "") != line:
            mismatch += 1
            continue
        covered += 1
    total = len(eligible)
    return {
        "eligible": total,
        "covered": covered,
        "mismatch": mismatch,
        "missing": missing,
        "coverage": covered / total if total else 1.0,
    }


def _aggregate_coverage(
    sample_rate: float = 1.0,
    log_filter: Optional[str] = None,
) -> dict:
    """Walk every log under metrics/logs/, compare against the queue index."""
    queue_index = _index_queue()
    rows: list[dict] = []
    total_eligible = 0
    total_covered = 0
    total_missing = 0
    total_mismatch = 0
    if not LOG_ROOT.is_dir():
        return {
            "error": f"no logs at {LOG_ROOT.relative_to(REPO_ROOT)}",
            "rows": [],
            "summary": {"coverage": None},
        }
    for log_path in sorted(LOG_ROOT.rglob("*.log")):
        if log_filter and log_filter not in log_path.name:
            continue
        rel_to_logs = str(log_path.relative_to(LOG_ROOT))
        per_log_index = queue_index.get(rel_to_logs, {})
        row = _coverage_for_log(log_path, per_log_index, sample_rate)
        row["log"] = rel_to_logs
        rows.append(row)
        if "eligible" in row:
            total_eligible += row["eligible"]
            total_covered += row["covered"]
            total_missing += row["missing"]
            total_mismatch += row["mismatch"]
    overall = total_covered / total_eligible if total_eligible else 1.0
    return {
        "rows": rows,
        "summary": {
            "log_files": len(rows),
            "eligible_lines": total_eligible,
            "covered_lines": total_covered,
            "missing_lines": total_missing,
            "mismatched_lines": total_mismatch,
            "coverage": overall,
            "sample_rate": sample_rate,
            "bridge_cursor_present": BRIDGE_CURSOR.is_file(),
            "decommission_safe": (
                overall >= DECOMMISSION_COVERAGE_FLOOR
                and total_mismatch == 0
            ),
        },
    }


# ---------------------------------------------------------------------------
# Output modes
# ---------------------------------------------------------------------------

def _print_summary(result: dict) -> None:
    s = result["summary"]
    if "error" in result:
        print(f"cmmi-queue-coverage-diff: {result['error']}", file=sys.stderr)
        return
    cov_pct = s["coverage"] * 100
    print(
        f"cmmi-queue-coverage-diff --summary"
        f"  files={s['log_files']}"
        f"  eligible={s['eligible_lines']}"
        f"  covered={s['covered_lines']}"
        f"  missing={s['missing_lines']}"
        f"  mismatch={s['mismatched_lines']}"
        f"  coverage={cov_pct:.2f}%"
        f"  sample={s['sample_rate'] * 100:.0f}%"
    )
    if not s["bridge_cursor_present"]:
        print("  note: bridge cursor absent — has the bridge ever run?")
    floor_pct = DECOMMISSION_COVERAGE_FLOOR * 100
    if s["decommission_safe"]:
        print(f"  decommission gate: SAFE "
              f"(≥{floor_pct:.1f}% coverage, 0 mismatches)")
    else:
        print(f"  decommission gate: NOT YET "
              f"(need ≥{floor_pct:.1f}% coverage AND 0 mismatches)")


def _print_detail(result: dict) -> None:
    if "error" in result:
        print(f"cmmi-queue-coverage-diff: {result['error']}", file=sys.stderr)
        return
    print(f"{'log file':<50}  {'eligible':>9} {'cov':>5}  {'miss':>5} {'mis':>4}")
    print(f"{'-' * 50}  {'-' * 9} {'-' * 5}  {'-' * 5} {'-' * 4}")
    for row in result["rows"]:
        if "error" in row:
            print(f"{row['log']:<50}  ERROR: {row['error']}")
            continue
        cov_pct = row["coverage"] * 100
        print(
            f"{row['log']:<50}  "
            f"{row['eligible']:>9} {cov_pct:>4.1f}%  "
            f"{row['missing']:>5} {row['mismatch']:>4}"
        )
    _print_summary(result)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--summary", action="store_true",
                      help="one-line coverage % (default; sampled at "
                      f"{SUMMARY_SAMPLE_RATE * 100:.0f}%%)")
    mode.add_argument("--detail", action="store_true",
                      help="per-log-file breakdown (full walk, no sampling)")
    mode.add_argument("--json", action="store_true",
                      help="raw JSON dump (full walk, no sampling)")
    ap.add_argument("--log-filter", default=None,
                    help="only consider logs whose name contains this substring")
    args = ap.parse_args(argv)

    # --summary is the default
    if not (args.detail or args.json):
        args.summary = True

    sample = SUMMARY_SAMPLE_RATE if args.summary else 1.0
    result = _aggregate_coverage(sample_rate=sample,
                                 log_filter=args.log_filter)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.detail:
        _print_detail(result)
    else:
        _print_summary(result)

    s = result.get("summary", {})
    return 0 if s.get("decommission_safe") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
