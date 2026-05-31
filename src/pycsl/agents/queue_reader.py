"""queue_reader — read agent messages from projects/pycsl/message-queues/.

Library used by `agent-feature-supervisor.py` (Item 3.4 cutover) and
any future consumer of the bridged message queue. Mirror counterpart
to `bin/cmmi-msg-bridge.py` (the writer).

The queue layout (per `bin/cmmi-msg-bridge.py`):

    projects/pycsl/message-queues/
    ├── .bridge-cursor.json          # bridge state, not a message
    ├── <agent-1>/
    │   └── inbox-from-logs/
    │       ├── <16-hex-uid>.json
    │       └── ...
    ├── <agent-2>/...

Each .json file is a `pycsl-cmmi-bridge-v1` message:

    {
      "schema": "pycsl-cmmi-bridge-v1",
      "uid": "<16-hex>",
      "source_uri": "metrics/logs/<file>:<lineno>",
      "agent": "<agent-name>",
      "ingested_at": "<UTC ISO8601>",
      "line_text": "<original log line>"
    }

This module is pure read; never writes inside `projects/pycsl/message-queues/`.

Per cmmi-tailoring-plan-follow-up-2.md Item 3.2.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from typing import Iterator, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent
QUEUE_ROOT = _PROJECT_ROOT / "projects" / "pycsl" / "message-queues"

EXPECTED_SCHEMA = "pycsl-cmmi-bridge-v1"


class InvalidMessage(ValueError):
    """Raised when a queue file doesn't validate against the schema field."""


def _agent_dir(agent: str) -> Path:
    return QUEUE_ROOT / agent / "inbox-from-logs"


def _parse_ingested(msg: dict) -> Optional[_dt.datetime]:
    raw = msg.get("ingested_at")
    if not isinstance(raw, str):
        return None
    try:
        # Allow trailing "Z" — Python's fromisoformat accepts it on 3.11+
        return _dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def agents() -> list[str]:
    """Enumerate every agent that has a non-empty inbox."""
    if not QUEUE_ROOT.is_dir():
        return []
    out: list[str] = []
    for d in sorted(QUEUE_ROOT.iterdir()):
        if not d.is_dir():
            continue
        inbox = d / "inbox-from-logs"
        if inbox.is_dir() and any(inbox.glob("*.json")):
            out.append(d.name)
    return out


def read_message(uid: str, agent: Optional[str] = None) -> Optional[dict]:
    """Look up a message by uid. If agent is given, scope the search."""
    if agent:
        candidates = [_agent_dir(agent) / f"{uid}.json"]
    else:
        if not QUEUE_ROOT.is_dir():
            return None
        candidates = list(QUEUE_ROOT.glob(f"*/inbox-from-logs/{uid}.json"))
    for p in candidates:
        if p.is_file():
            return _load_and_validate(p)
    return None


def _load_and_validate(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise InvalidMessage(f"{path}: {e}") from e
    if not isinstance(data, dict):
        raise InvalidMessage(f"{path}: top-level value is not an object")
    schema = data.get("schema")
    if schema != EXPECTED_SCHEMA:
        raise InvalidMessage(
            f"{path}: schema mismatch — expected {EXPECTED_SCHEMA!r}, "
            f"got {schema!r}"
        )
    return data


def iter_messages(
    agent: str,
    since: Optional[_dt.datetime] = None,
    *,
    strict: bool = False,
) -> Iterator[dict]:
    """Yield messages for `agent` in deterministic uid-order.

    Parameters
    ----------
    agent:
        Agent inbox to walk. Must match the directory name written by
        the bridge (`agent_from_log` in cmmi-msg-bridge.py — the .log
        stem).
    since:
        If given, skip messages whose `ingested_at` is earlier than
        this datetime. Naive datetimes are treated as UTC.
    strict:
        If True, raise InvalidMessage on schema mismatch. Default
        False — invalid messages are silently skipped (useful for
        operational mode where partial corruption shouldn't abort
        the consumer).
    """
    inbox = _agent_dir(agent)
    if not inbox.is_dir():
        return
    # Sort by filename (16-hex uid) for stable, deterministic order.
    # This is NOT chronological — the bridge writes uid as a hash of
    # source_uri + line_text. Callers needing chronological order
    # should sort by `ingested_at` after collecting.
    if since is not None and since.tzinfo is None:
        since = since.replace(tzinfo=_dt.timezone.utc)
    for p in sorted(inbox.glob("*.json"), key=lambda x: x.name):
        try:
            msg = _load_and_validate(p)
        except InvalidMessage:
            if strict:
                raise
            continue
        if since is not None:
            ts = _parse_ingested(msg)
            if ts is not None and ts < since:
                continue
        yield msg


def count_messages(agent: Optional[str] = None) -> int:
    """Return the number of messages in `agent`'s inbox (or all if None)."""
    if agent:
        inbox = _agent_dir(agent)
        return sum(1 for _ in inbox.glob("*.json")) if inbox.is_dir() else 0
    if not QUEUE_ROOT.is_dir():
        return 0
    return sum(1 for _ in QUEUE_ROOT.glob("*/inbox-from-logs/*.json"))


__all__ = [
    "InvalidMessage",
    "EXPECTED_SCHEMA",
    "QUEUE_ROOT",
    "agents",
    "count_messages",
    "iter_messages",
    "read_message",
]
