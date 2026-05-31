"""Item 3.4t — tests for _read_agent_log_context queue-first/log-fallback.

The supervisor's new reader has three branches:
  1. Queue has data for the agent → return queue line_text strings.
  2. Queue is empty AND bridge cursor missing → fall back to
     metrics/logs/<agent>.log if present.
  3. Queue is empty AND bridge cursor present → return [] (do NOT
     fall back to logs — the bridge has run, an empty queue means
     the agent legitimately has no recent activity).

These tests patch QUEUE_ROOT / _BRIDGE_CURSOR / _METRICS_LOGS to
tmp_path so we exercise each branch in isolation.

Per cmmi-tailoring-plan-follow-up-3.md Item 3.4t.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "pycsl" / "agents"))

# Dynamic import — module file name has `-`
_SPEC = importlib.util.spec_from_file_location(
    "agent_feature_supervisor",
    REPO_ROOT / "src" / "pycsl" / "agents" / "agent-feature-supervisor.py",
)
assert _SPEC is not None and _SPEC.loader is not None
sup = importlib.util.module_from_spec(_SPEC)
sys.modules["agent_feature_supervisor"] = sup
_SPEC.loader.exec_module(sup)

import queue_reader  # noqa: E402


@pytest.fixture
def fake_env(tmp_path, monkeypatch):
    """Point supervisor and queue_reader at tmp_path-based scratch dirs."""
    queue_root = tmp_path / "message-queues"
    metrics_logs = tmp_path / "metrics-logs"
    bridge_cursor = queue_root / ".bridge-cursor.json"
    queue_root.mkdir()
    metrics_logs.mkdir()

    monkeypatch.setattr(queue_reader, "QUEUE_ROOT", queue_root)
    monkeypatch.setattr(sup, "_BRIDGE_CURSOR", bridge_cursor)
    monkeypatch.setattr(sup, "_METRICS_LOGS", metrics_logs)

    def add_queue_msg(agent: str, uid: str, line_text: str) -> None:
        inbox = queue_root / agent / "inbox-from-logs"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / f"{uid}.json").write_text(json.dumps({
            "schema": queue_reader.EXPECTED_SCHEMA,
            "uid": uid,
            "source_uri": f"metrics/logs/{agent}.log:1",
            "agent": agent,
            "ingested_at": "2026-05-31T12:00:00Z",
            "line_text": line_text,
        }))

    def write_log(agent: str, body: str) -> None:
        (metrics_logs / f"{agent}.log").write_text(body)

    def write_cursor() -> None:
        bridge_cursor.write_text(json.dumps({"sentinel": "bridge-has-run"}))

    return type("FakeEnv", (), {
        "queue_root": queue_root,
        "metrics_logs": metrics_logs,
        "bridge_cursor": bridge_cursor,
        "add_queue_msg": staticmethod(add_queue_msg),
        "write_log": staticmethod(write_log),
        "write_cursor": staticmethod(write_cursor),
    })


# ---------------------------------------------------------------------------
# Branch 1: queue has data → use it
# ---------------------------------------------------------------------------

def test_queue_first_when_queue_has_data(fake_env):
    fake_env.add_queue_msg("agent-alpha", "0000000000000001", "line from queue 1")
    fake_env.add_queue_msg("agent-alpha", "0000000000000002", "line from queue 2")
    # Even with metrics/logs/ also containing data, queue wins
    fake_env.write_log("agent-alpha", "should not be returned\n")
    fake_env.write_cursor()

    lines = sup._read_agent_log_context("agent-alpha", max_messages=5)
    assert lines == ["line from queue 1", "line from queue 2"], (
        f"queue-first: expected the 2 queue lines, got {lines!r}"
    )


# ---------------------------------------------------------------------------
# Branch 2: queue empty + cursor missing → fall back to metrics/logs/
# ---------------------------------------------------------------------------

def test_fallback_to_logs_when_queue_empty_and_no_cursor(fake_env):
    # Queue has nothing for agent-beta; no bridge cursor
    fake_env.write_log("agent-beta", "log line A\nlog line B\n\nlog line C\n")

    lines = sup._read_agent_log_context("agent-beta", max_messages=5)
    assert lines == ["log line A", "log line B", "log line C"], (
        f"log-fallback: expected 3 non-blank lines, got {lines!r}"
    )


def test_fallback_respects_max_messages(fake_env):
    body = "\n".join(f"line {i}" for i in range(20)) + "\n"
    fake_env.write_log("agent-gamma", body)

    lines = sup._read_agent_log_context("agent-gamma", max_messages=3)
    assert len(lines) == 3
    # Fallback returns LAST `max_messages` non-blank lines (most recent)
    assert lines == ["line 17", "line 18", "line 19"]


# ---------------------------------------------------------------------------
# Branch 3: queue empty + cursor present → return [] (don't mask bridge breakage)
# ---------------------------------------------------------------------------

def test_no_fallback_when_bridge_cursor_exists(fake_env):
    # Bridge has run (cursor exists) but agent's queue is empty.
    # metrics/logs/ has data — should NOT be returned (would mask
    # bridge breakage).
    fake_env.write_cursor()
    fake_env.write_log("agent-delta", "stale log content from before bridge\n")

    lines = sup._read_agent_log_context("agent-delta", max_messages=5)
    assert lines == [], (
        "When bridge cursor exists and queue is empty, must return [] "
        "without falling back to metrics/logs/ — fallback would mask "
        "bridge breakage. Got: " + repr(lines)
    )


def test_returns_empty_when_neither_source_has_data(fake_env):
    # No cursor, no queue messages, no log file
    lines = sup._read_agent_log_context("agent-nonexistent", max_messages=5)
    assert lines == []
