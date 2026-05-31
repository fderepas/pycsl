"""Item 3.3 — synthetic-queue tests for queue_reader.py.

These tests don't depend on the live bridge contents. They build a
small fixture queue in tmp_path and verify the reader's contract:
schema validation, deterministic ordering, agent enumeration,
since-filter, missing-schema rejection.

Per cmmi-tailoring-plan-follow-up-2.md Item 3.3.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "pycsl" / "agents"))

import queue_reader  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_msg(uid: str, agent: str, source_uri: str, line_text: str,
              ingested: str = "2026-05-31T12:00:00Z") -> dict:
    return {
        "schema": queue_reader.EXPECTED_SCHEMA,
        "uid": uid,
        "source_uri": source_uri,
        "agent": agent,
        "ingested_at": ingested,
        "line_text": line_text,
    }


@pytest.fixture
def fake_queue(tmp_path, monkeypatch):
    """Build a synthetic queue under tmp_path and point queue_reader at it."""
    queue_root = tmp_path / "message-queues"

    def add(agent: str, uid: str, **overrides) -> Path:
        inbox = queue_root / agent / "inbox-from-logs"
        inbox.mkdir(parents=True, exist_ok=True)
        msg = _make_msg(uid, agent, f"metrics/logs/{agent}.log:1",
                        f"line content for {uid}")
        msg.update(overrides)
        p = inbox / f"{uid}.json"
        p.write_text(json.dumps(msg))
        return p

    # Standard synthetic queue: 2 agents, 5 messages
    add("test-agent-alpha", "0000000000000001")
    add("test-agent-alpha", "0000000000000002",
        ingested_at="2026-05-31T12:00:10Z")
    add("test-agent-alpha", "0000000000000003",
        ingested_at="2026-05-31T12:00:20Z")
    add("test-agent-beta", "0000000000000004")
    add("test-agent-beta", "0000000000000005")

    monkeypatch.setattr(queue_reader, "QUEUE_ROOT", queue_root)
    return queue_root, add


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_agents_enumerates_only_non_empty_inboxes(fake_queue, tmp_path):
    queue_root, add = fake_queue
    # An empty inbox should NOT appear in agents()
    (queue_root / "empty-agent" / "inbox-from-logs").mkdir(parents=True)
    ags = queue_reader.agents()
    assert "test-agent-alpha" in ags
    assert "test-agent-beta" in ags
    assert "empty-agent" not in ags, (
        "Empty inboxes should be filtered — they are noise for consumers"
    )


def test_iter_messages_returns_validated_schema(fake_queue):
    msgs = list(queue_reader.iter_messages("test-agent-alpha"))
    assert len(msgs) == 3
    assert all(m["schema"] == queue_reader.EXPECTED_SCHEMA for m in msgs)
    assert all(m["agent"] == "test-agent-alpha" for m in msgs)


def test_iter_messages_deterministic_by_uid(fake_queue):
    """uids sort alphanumerically for stable iteration order."""
    uids = [m["uid"] for m in queue_reader.iter_messages("test-agent-alpha")]
    assert uids == sorted(uids), (
        "iter_messages must return messages in uid sort order — consumers "
        "rely on deterministic order for resume semantics."
    )


def test_iter_messages_unknown_agent_returns_empty(fake_queue):
    msgs = list(queue_reader.iter_messages("does-not-exist"))
    assert msgs == []


def test_iter_messages_since_filter(fake_queue):
    """since= drops messages ingested before the cutoff."""
    cutoff = _dt.datetime(2026, 5, 31, 12, 0, 15, tzinfo=_dt.timezone.utc)
    msgs = list(queue_reader.iter_messages("test-agent-alpha", since=cutoff))
    # 3 messages at :00, :10, :20 — only :20 should survive
    assert len(msgs) == 1
    assert msgs[0]["uid"] == "0000000000000003"


def test_iter_messages_skips_invalid_by_default(fake_queue):
    """Non-strict mode silently skips schema-mismatched messages."""
    queue_root, add = fake_queue
    # Write a bad message in test-agent-beta's inbox
    bad = queue_root / "test-agent-beta" / "inbox-from-logs" / "bad.json"
    bad.write_text(json.dumps({"schema": "wrong-schema", "uid": "bad"}))
    msgs = list(queue_reader.iter_messages("test-agent-beta"))
    uids = [m["uid"] for m in msgs]
    assert "bad" not in uids
    assert len(msgs) == 2  # only the 2 valid messages


def test_iter_messages_strict_raises_on_invalid(fake_queue):
    """strict=True surfaces schema mismatches as exceptions."""
    queue_root, add = fake_queue
    bad = queue_root / "test-agent-beta" / "inbox-from-logs" / "bad.json"
    bad.write_text(json.dumps({"schema": "wrong-schema", "uid": "bad"}))
    with pytest.raises(queue_reader.InvalidMessage):
        list(queue_reader.iter_messages("test-agent-beta", strict=True))


def test_read_message_by_uid(fake_queue):
    """read_message looks up by uid; scoped or global."""
    m = queue_reader.read_message("0000000000000002", agent="test-agent-alpha")
    assert m is not None
    assert m["uid"] == "0000000000000002"
    # Global lookup also works
    m2 = queue_reader.read_message("0000000000000004")
    assert m2 is not None
    assert m2["agent"] == "test-agent-beta"
    # Missing uid returns None
    assert queue_reader.read_message("does-not-exist") is None


def test_count_messages(fake_queue):
    assert queue_reader.count_messages("test-agent-alpha") == 3
    assert queue_reader.count_messages("test-agent-beta") == 2
    assert queue_reader.count_messages() == 5  # global


def test_round_trip_against_bridge_schema(fake_queue):
    """Sanity: messages we write match what bin/cmmi-msg-bridge.py produces."""
    queue_root, add = fake_queue
    msgs = list(queue_reader.iter_messages("test-agent-alpha"))
    required_fields = {"schema", "uid", "source_uri", "agent",
                       "ingested_at", "line_text"}
    for m in msgs:
        missing = required_fields - set(m)
        assert not missing, f"message missing fields: {missing}"
        assert m["schema"] == "pycsl-cmmi-bridge-v1"
