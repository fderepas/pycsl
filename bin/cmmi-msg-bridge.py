#!/usr/bin/env python3
"""cmmi-msg-bridge — one-way mirror metrics/logs/ → projects/pycsl/message-queues/.

Phase 1 of the communication-skill transition (per
cmmi-tailoring-plan.md §10): bridge existing coordinator log lines
into the file-based message-queues/ substrate without changing agent
behaviour. Each metrics/logs/<agent>.log becomes a per-agent inbox
of JSON messages that reference the source line.

Anti-duplication: messages carry a `source_uri` like
`metrics/logs/coordinator.log:1542` — the bridge never copies log
content into the queue; it stores pointers + the line text.

Modes:
    cmmi-msg-bridge.py                        # incremental sync since last run
    cmmi-msg-bridge.py --rebuild              # wipe queue and rebuild
    cmmi-msg-bridge.py --dry-run              # report what would change
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_ROOT = REPO_ROOT / "metrics" / "logs"
QUEUE_ROOT = REPO_ROOT / "projects" / "pycsl" / "message-queues"
CURSOR_FILE = QUEUE_ROOT / ".bridge-cursor.json"


def utc_iso() -> str:
    return (
        _dt.datetime.now(_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def agent_from_log(log_path: Path) -> str:
    """Derive the agent name from a log file name (strip .log, normalise)."""
    return log_path.stem


def line_uid(source_uri: str, line_text: str) -> str:
    """Stable id from source_uri + line content (hash, 16 hex chars)."""
    h = hashlib.sha256(f"{source_uri}\n{line_text}".encode()).hexdigest()
    return h[:16]


def load_cursor() -> dict[str, int]:
    if not CURSOR_FILE.is_file():
        return {}
    try:
        return json.loads(CURSOR_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_cursor(cursor: dict[str, int]) -> None:
    CURSOR_FILE.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_FILE.write_text(json.dumps(cursor, indent=2, sort_keys=True))


def sync(rebuild: bool, dry_run: bool, max_age_days: int | None) -> int:
    if not LOG_ROOT.is_dir():
        print(
            f"cmmi-msg-bridge: no logs at {LOG_ROOT.relative_to(REPO_ROOT)} — nothing to bridge",
            file=sys.stderr,
        )
        return 0
    if rebuild and not dry_run:
        # Only wipe the bridge-managed inboxes; leave anything else alone.
        for inbox in QUEUE_ROOT.glob("*/inbox-from-logs"):
            for f in inbox.glob("*.json"):
                f.unlink()
        if CURSOR_FILE.is_file():
            CURSOR_FILE.unlink()
    cursor = {} if rebuild else load_cursor()
    new_msgs = 0
    touched_agents: set[str] = set()
    skipped_old = 0
    cutoff_ts: float | None = None
    if max_age_days is not None and max_age_days > 0:
        import time
        cutoff_ts = time.time() - max_age_days * 86400.0
    for log in sorted(LOG_ROOT.rglob("*.log")):
        # 3.1a: bound volume by skipping log files whose mtime is
        # older than --max-age-days. Cursor still advances when the
        # file is processed in a later run; old files are simply
        # left un-mirrored (they're already in metrics/logs/ for
        # backward-compat human inspection).
        if cutoff_ts is not None:
            try:
                if log.stat().st_mtime < cutoff_ts:
                    skipped_old += 1
                    continue
            except OSError:
                continue
        agent = agent_from_log(log)
        try:
            lines = log.read_text().splitlines()
        except UnicodeDecodeError:
            continue
        last_seen = cursor.get(agent, 0)
        if len(lines) <= last_seen:
            continue
        inbox = QUEUE_ROOT / agent / "inbox-from-logs"
        if not dry_run:
            inbox.mkdir(parents=True, exist_ok=True)
        for i in range(last_seen, len(lines)):
            line_text = lines[i]
            if not line_text.strip():
                continue
            source_uri = f"metrics/logs/{log.relative_to(LOG_ROOT)}:{i + 1}"
            uid = line_uid(source_uri, line_text)
            msg = {
                "schema": "pycsl-cmmi-bridge-v1",
                "uid": uid,
                "source_uri": source_uri,
                "agent": agent,
                "ingested_at": utc_iso(),
                "line_text": line_text,
            }
            if not dry_run:
                (inbox / f"{uid}.json").write_text(
                    json.dumps(msg, indent=2, sort_keys=True)
                )
            new_msgs += 1
            touched_agents.add(agent)
        cursor[agent] = len(lines)
    if not dry_run:
        save_cursor(cursor)
    verb = "would write" if dry_run else "wrote"
    age_clause = (
        f" (skipped {skipped_old} log files older than "
        f"{max_age_days} days)"
        if skipped_old
        else ""
    )
    print(
        f"cmmi-msg-bridge: {verb} {new_msgs} new messages across "
        f"{len(touched_agents)} agents{age_clause}"
    )
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Mirror metrics/logs/ → projects/pycsl/message-queues/."
    )
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--max-age-days",
        type=int,
        default=30,
        help="Only mirror log files whose mtime is within N days "
        "(default 30; 0 disables the cutoff). Bounds bridge volume "
        "for daily cron runs.",
    )
    args = ap.parse_args(argv)
    max_age = args.max_age_days if args.max_age_days > 0 else None
    return sync(
        rebuild=args.rebuild,
        dry_run=args.dry_run,
        max_age_days=max_age,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
