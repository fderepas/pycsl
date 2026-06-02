#!/usr/bin/env python3
"""cmmi-metrics-ingest — normalise metrics/ tree into per-system KPIs.

Reads the existing metrics/ tree (logs, monitor, evaluator, reviewer
outputs from coordinator.py + meta-agents) and emits a per-system
normalised snapshot to:

    projects/pycsl/docs/metrics/metrics-store.json

References source data via `source_uri` fields — never duplicates.

Per cmmi-tailoring-plan.md §7 (cmmi-metrics-collection tailoring).

Modes:
    cmmi-metrics-ingest.py                  # one-shot snapshot
    cmmi-metrics-ingest.py --weekly         # append weekly row to time series
    cmmi-metrics-ingest.py --show           # print last snapshot

The current MVP collects a small KPI set; richer metrics (proof-success
rate per system per week, agent retry-count drift, doc-coherency
events / week) are added incrementally per the QPM Phase 0 snapshot
accumulation requirement.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
METRICS_SRC = REPO_ROOT / "metrics"
STORE_DIR = REPO_ROOT / "projects" / "pycsl" / "docs" / "metrics"
STORE_FILE = STORE_DIR / "metrics-store.json"
PROJECT_MD = REPO_ROOT / "projects" / "pycsl" / "PROJECT.md"

SYSTEM_ROW_RE = re.compile(
    r"\|\s*(SY\d)\s*\|\s*([A-Za-z0-9_]+)\s*\|.*?\|\s*`([^`]+)/`\s*\|"
)


def discover_systems() -> list[tuple[str, str, Path]]:
    text = PROJECT_MD.read_text()
    return [
        (m.group(1), m.group(2), REPO_ROOT / m.group(3))
        for m in SYSTEM_ROW_RE.finditer(text)
    ]


def utc_iso() -> str:
    # naive, file-system clock — used only as a snapshot label
    try:
        # Python clocks would normally be forbidden in workflow scripts;
        # here we are a CLI tool, so it's fine.
        return (
            _dt.datetime.now(_dt.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
    except Exception:
        return "unknown"


def count_lines(p: Path) -> int:
    try:
        return sum(1 for _ in p.open())
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# 4.1B prep — KPI collectors for cmmi-qpm-charts.py
# ---------------------------------------------------------------------------
#
# Each returns either a float/int KPI value, or None when not yet
# observable (early snapshots, missing tooling). Downstream chart
# tool tolerates None gracefully via "weak signal" mode.

def _recent_log_files(window_days: float = 7.0) -> list[Path]:
    """Logs whose mtime is within the last `window_days` days."""
    logs_dir = METRICS_SRC / "logs"
    if not logs_dir.is_dir():
        return []
    try:
        import time
        cutoff = time.time() - window_days * 86400.0
    except Exception:
        return []
    out: list[Path] = []
    for p in logs_dir.rglob("*.log"):
        try:
            if p.stat().st_mtime >= cutoff:
                out.append(p)
        except OSError:
            pass
    return out


_PYCSL_PROOF_PASS_RE = re.compile(r"\bpycsl\b.*--proof.*\bPASS\b", re.I)
_PYCSL_PROOF_FAIL_RE = re.compile(r"\bpycsl\b.*--proof.*\bFAIL\b", re.I)
_RETRY_RE = re.compile(r"\b(retry|retries|attempt)\b[^\n]{0,40}?(\d+)", re.I)


def _collect_pycsl_proof_pass_rate(
    sy_id: str, src_root: Path, window_days: float = 7.0
) -> dict:
    """Pass-rate of `pycsl --proof` invocations attributable to this system.

    Heuristic: scan recent log lines for PASS/FAIL markers that
    mention this system's src path (e.g. `src/pycsl_lib/`). Returns
    {pass: int, fail: int, rate: float | None, observed: bool}.
    Returns observed=False when the system contributes no proof
    activity in the window (rate is None then).
    """
    if not src_root.is_dir():
        return {"pass": 0, "fail": 0, "rate": None, "observed": False}
    src_marker = str(src_root.relative_to(REPO_ROOT))
    name_marker = src_root.name  # e.g. "pycsl_lib"
    p = 0
    f = 0
    for log in _recent_log_files(window_days):
        try:
            text = log.read_text(errors="replace")
        except OSError:
            continue
        if src_marker not in text and name_marker not in text:
            continue
        p += len(_PYCSL_PROOF_PASS_RE.findall(text))
        f += len(_PYCSL_PROOF_FAIL_RE.findall(text))
    total = p + f
    rate = (p / total) if total > 0 else None
    return {
        "pass": p,
        "fail": f,
        "rate": rate,
        "observed": total > 0,
    }


def _collect_coordinator_retries(window_days: float = 7.0) -> dict:
    """Average retry/attempt count across recent coordinator log lines.

    Returns {samples: int, avg: float | None, max: int | None}.
    """
    samples: list[int] = []
    for log in _recent_log_files(window_days):
        if "coordinator" not in log.name.lower():
            continue
        try:
            text = log.read_text(errors="replace")
        except OSError:
            continue
        for m in _RETRY_RE.finditer(text):
            try:
                samples.append(int(m.group(2)))
            except ValueError:
                continue
    if not samples:
        return {"samples": 0, "avg": None, "max": None}
    return {
        "samples": len(samples),
        "avg": sum(samples) / len(samples),
        "max": max(samples),
    }


def _count_doc_coherency_events(window_days: float = 7.0) -> dict:
    """Count `doc-coherency.py` invocations + non-zero exits in window.

    The current bin/doc-coherency.py doesn't write its own log;
    cron and CI redirect to metrics/cron.log. We look there for
    invocation markers.
    """
    cron_log = METRICS_SRC / "cron.log"
    if not cron_log.is_file():
        return {"invocations": 0, "failures": 0, "observed": False}
    try:
        import time
        cutoff = time.time() - window_days * 86400.0
        if cron_log.stat().st_mtime < cutoff:
            return {"invocations": 0, "failures": 0, "observed": False}
        text = cron_log.read_text(errors="replace")
    except OSError:
        return {"invocations": 0, "failures": 0, "observed": False}
    invocations = len(re.findall(r"doc-coherency", text))
    # Heuristic: a doc-coherency failure manifests as a line with
    # "FAIL" or "exit 1" in proximity (cron output isn't structured).
    failures = len(re.findall(
        r"doc-coherency[^\n]{0,200}(FAIL|exit\s*1|exit\s*[2-9])",
        text, re.I,
    ))
    return {
        "invocations": invocations,
        "failures": failures,
        "observed": invocations > 0,
    }


def _mean_max(xs: list) -> dict:
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"avg": None, "max": None, "samples": 0}
    return {"avg": round(sum(xs) / len(xs), 3), "max": max(xs), "samples": len(xs)}


def _rate(num: int, den: int):
    return round(num / den, 4) if den else None


def collect_agent_loop_kpis() -> dict:
    """CMMI L4 agent-ecosystem KPIs, aggregated from the per-run summaries the
    coordinator (metrics/run-summary/) and feature-supervisor
    (metrics/feature-supervisor/<slug>/run-summary.json) emit.

    Record-only: no control limits here — `cmmi-quantitative-mgmt` derives μ±3σ
    once >=8 weekly snapshots accumulate. See
    config/skills/cmmi-metrics-collection/references/agent-loop-kpis.md.
    """
    rs_dir = METRICS_SRC / "run-summary"
    fs_dir = METRICS_SRC / "feature-supervisor"

    # ---- Annotation-loop axis (coordinator) ----
    attempts_used, halts = [], {"max-retries": 0, "loop-detected": 0, "ping-pong": 0}
    redecompose_total = files = needing_reconcile = first_fix = 0
    fc_by_class: dict = {}
    fc_overall = {"correct": 0, "total": 0}
    rocq = {"generated": 0, "completed": 0, "aborted": 0, "incomplete": 0}
    rocq_retries: list = []
    if rs_dir.is_dir():
        for f in sorted(rs_dir.glob("*.json")):
            try:
                s = json.loads(f.read_text())
            except Exception:
                continue
            files += 1
            attempts_used.append(s.get("attempts_used"))
            if s.get("outcome") in halts:
                halts[s["outcome"]] += 1
            loop = s.get("loop") or {}
            redecompose_total += loop.get("redecompose_count", 0) or 0
            if (s.get("attempts_used") or 0) >= 2:
                needing_reconcile += 1
                if s.get("outcome") == "passed" and s.get("attempts_used") == 2:
                    first_fix += 1
            fc = (s.get("fault_correctness") or {})
            for cls, d in (fc.get("by_class") or {}).items():
                slot = fc_by_class.setdefault(cls, {"correct": 0, "total": 0})
                slot["correct"] += d.get("correct", 0)
                slot["total"] += d.get("total", 0)
            ov = fc.get("overall") or {}
            fc_overall["correct"] += ov.get("correct", 0)
            fc_overall["total"] += ov.get("total", 0)
            rq = s.get("rocq") or {}
            for k in ("generated", "completed", "aborted", "incomplete"):
                rocq[k] += rq.get(k, 0) or 0
            for ob in (rq.get("obligations") or []):
                if ob.get("retries") is not None:
                    rocq_retries.append(ob["retries"])
    for cls, d in fc_by_class.items():
        d["rate"] = _rate(d["correct"], d["total"])

    # ---- Feature-rollout axis (supervisor) ----
    runs = acc_passed = acc_total = delegated = rolled_back = lb_halts = 0
    status_forged = 0
    gate_pass = gate_fail = 0
    rocq_citations = 0
    if fs_dir.is_dir():
        for f in sorted(fs_dir.glob("*/run-summary.json")):
            try:
                s = json.loads(f.read_text())
            except Exception:
                continue
            runs += 1
            if str(s.get("outcome", "")).startswith("halted-STATUS_FORGED"):
                status_forged += 1
            if s.get("outcome") == "halted-load-bearing":
                lb_halts += 1
            for ph in s.get("phases", []):
                ac = ph.get("acceptance") or {}
                acc_passed += ac.get("passed", 0) or 0
                acc_total += ac.get("total", 0) or 0
                if ph.get("rocq_citations"):
                    rocq_citations += ph["rocq_citations"]
            t = s.get("totals") or {}
            delegated += t.get("delegated", 0) or 0
            rolled_back += t.get("rolled_back", 0) or 0
            for g in s.get("gate", []):
                if g.get("skipped"):
                    continue
                if g.get("passed"):
                    gate_pass += 1
                else:
                    gate_fail += 1

    return {
        "annotation_loop": {
            "files": files,
            "convergence_attempts": _mean_max(attempts_used),
            "loop_detect_rate": _rate(halts["loop-detected"] + halts["ping-pong"], files),
            "redecompose_rate": _rate(redecompose_total, files),
            "first_fix_yield": _rate(first_fix, needing_reconcile),
            "fault_correctness": {
                "by_class": fc_by_class,
                "overall": {**fc_overall, "rate": _rate(fc_overall["correct"], fc_overall["total"])},
            },
            "rocq": {
                **rocq,
                "completion_rate": _rate(rocq["completed"], rocq["generated"]),
                "abort_rate": _rate(rocq["aborted"], rocq["generated"]),
                "retries": _mean_max(rocq_retries),
            },
            "source_uri": str(rs_dir.relative_to(REPO_ROOT)) if rs_dir.is_dir() else None,
        },
        "feature_rollout": {
            "runs": runs,
            "acceptance_passrate": _rate(acc_passed, acc_total),
            "gate_passrate": _rate(gate_pass, gate_pass + gate_fail),
            "delegation_rollback_rate": _rate(rolled_back, delegated),
            "loadbearing_halt_rate": _rate(lb_halts, runs),
            "status_forged_rate": _rate(status_forged, runs),
            "rocq_citations": rocq_citations,
            "source_uri": str(fs_dir.relative_to(REPO_ROOT)) if fs_dir.is_dir() else None,
        },
    }


def collect_global() -> dict:
    """KPIs that aren't per-system."""
    logs = METRICS_SRC / "logs"
    monitor = METRICS_SRC / "monitor"
    evaluator = METRICS_SRC / "evaluator"
    reviewer = METRICS_SRC / "reviewer"
    out = {
        "log_files": 0,
        "log_lines_total": 0,
        "monitor_reports": 0,
        "evaluator_reports": 0,
        "reviewer_reports": 0,
        "source_uri": {
            "logs": str(logs.relative_to(REPO_ROOT)) if logs.is_dir() else None,
            "monitor": str(monitor.relative_to(REPO_ROOT)) if monitor.is_dir() else None,
            "evaluator": str(evaluator.relative_to(REPO_ROOT)) if evaluator.is_dir() else None,
            "reviewer": str(reviewer.relative_to(REPO_ROOT)) if reviewer.is_dir() else None,
        },
    }
    if logs.is_dir():
        log_files = [p for p in logs.rglob("*.log") if p.is_file()]
        out["log_files"] = len(log_files)
        out["log_lines_total"] = sum(count_lines(p) for p in log_files)
    if monitor.is_dir():
        out["monitor_reports"] = sum(1 for _ in monitor.rglob("*.json")) + sum(
            1 for _ in monitor.rglob("*.md")
        )
    if evaluator.is_dir():
        out["evaluator_reports"] = sum(1 for _ in evaluator.rglob("*.json")) + sum(
            1 for _ in evaluator.rglob("*.md")
        )
    if reviewer.is_dir():
        out["reviewer_reports"] = sum(1 for _ in reviewer.rglob("*.json")) + sum(
            1 for _ in reviewer.rglob("*.md")
        )
    # 4.1B prep: new KPIs sourced from log content
    out["coordinator_retries_week"] = _collect_coordinator_retries(7.0)
    out["doc_coherency_events_week"] = _count_doc_coherency_events(7.0)
    # L4 agent-ecosystem KPIs from the per-run summaries.
    out["agent_loop_kpis"] = collect_agent_loop_kpis()
    return out


def collect_system(sy_id: str, name: str, src_root: Path) -> dict:
    """Per-system KPIs sourced from src/ surface inspection."""
    files = 0
    loc = 0
    contracts = 0
    cite_notes = 0  # L3-ceiling fallback markers (see better-agent.md Phase 1)
    if src_root.is_dir():
        for py in src_root.rglob("*.py"):
            if "__pycache__" in py.parts or ".egg-info" in str(py):
                continue
            files += 1
            try:
                text = py.read_text()
            except UnicodeDecodeError:
                continue
            loc += text.count("\n")
            contracts += len(re.findall(r"^\s*#@\s", text, re.M))
            cite_notes += len(re.findall(r"#\s*cite:_note\s*:", text))
    return {
        "id": sy_id,
        "name": name,
        "src": str(src_root.relative_to(REPO_ROOT))
        if src_root.is_dir()
        else None,
        "files": files,
        "loc": loc,
        "contract_lines": contracts,
        "l3_ceiling_notes": cite_notes,
        # 4.1B prep: per-system proof pass rate (None when not observed)
        "pycsl_proof_pass_rate_week": _collect_pycsl_proof_pass_rate(
            sy_id, src_root, 7.0
        ),
    }


def collect_doc_coherency() -> dict:
    """One-shot run of bin/doc-coherency.py --check to record current state."""
    tool = REPO_ROOT / "bin" / "doc-coherency.py"
    if not tool.is_file():
        return {"available": False}
    try:
        r = subprocess.run(
            [str(tool), "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "available": True,
            "exit_code": r.returncode,
            "stdout_lines": len(r.stdout.splitlines()),
            "stderr_lines": len(r.stderr.splitlines()),
        }
    except Exception as e:
        return {"available": True, "error": str(e)}


def snapshot() -> dict:
    systems = discover_systems()
    snap = {
        "timestamp": utc_iso(),
        "schema_version": 1,
        "global": collect_global(),
        "doc_coherency": collect_doc_coherency(),
        "systems": [
            collect_system(sy_id, name, src) for sy_id, name, src in systems
        ],
    }
    return snap


def load_store() -> dict:
    if not STORE_FILE.is_file():
        return {"snapshots": []}
    try:
        return json.loads(STORE_FILE.read_text())
    except json.JSONDecodeError:
        return {"snapshots": []}


def save_store(store: dict) -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    STORE_FILE.write_text(json.dumps(store, indent=2, sort_keys=True))


def cmd_one_shot() -> int:
    snap = snapshot()
    store = load_store()
    store["latest"] = snap
    save_store(store)
    print(
        f"cmmi-metrics-ingest: snapshot written -> "
        f"{STORE_FILE.relative_to(REPO_ROOT)}"
    )
    return 0


def cmd_weekly() -> int:
    snap = snapshot()
    store = load_store()
    store.setdefault("snapshots", []).append(snap)
    store["latest"] = snap
    save_store(store)
    print(
        f"cmmi-metrics-ingest: weekly snapshot appended "
        f"({len(store['snapshots'])} total)"
    )
    return 0


def cmd_show() -> int:
    store = load_store()
    if "latest" not in store:
        print("cmmi-metrics-ingest: no snapshot yet; run without --show first")
        return 1
    print(json.dumps(store["latest"], indent=2, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Normalise metrics/ tree to per-system KPIs."
    )
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--weekly", action="store_true")
    g.add_argument("--show", action="store_true")
    args = ap.parse_args(argv)

    if args.show:
        return cmd_show()
    if args.weekly:
        return cmd_weekly()
    return cmd_one_shot()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
