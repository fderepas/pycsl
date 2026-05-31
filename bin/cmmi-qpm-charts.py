#!/usr/bin/env python3
"""cmmi-qpm-charts — SPC control charts + Western Electric rule
detection for the per-system PyCSL KPIs.

Reads projects/pycsl/docs/metrics/metrics-store.json (built up by
weekly `bin/cmmi-metrics-ingest.py --weekly` snapshots). For each of
4 KPI series, extracts the time series across snapshots[],
computes μ + σ + control limits (UCL=μ+3σ, LCL=max(0, μ−3σ)),
and renders a Markdown table + ASCII spark-line per (KPI, system).

Three signal-strength modes (per cmmi-tailoring-plan-follow-up-2.md):
  * weak        — n < 8 snapshots: emit time series only, no limits
  * preliminary — 8 <= n < 20:    compute limits + WE rules, tag preliminary
  * stable      — n >= 20:        full strong-signal report

Western Electric rules (4.1C):
  WE1 — 1 point beyond ±3σ
  WE2 — 2 of 3 consecutive points beyond ±2σ on same side
  WE3 — 4 of 5 consecutive points beyond ±1σ on same side
  WE4 — 8 consecutive points on same side of μ

Per cmmi-tailoring-plan-follow-up-2.md Items 4.1B + 4.1C.

Modes:
  cmmi-qpm-charts.py           # emit fresh QPM report
  cmmi-qpm-charts.py --check   # informational summary; exit 0 always
                               # (called from bin/cmmi-audit.sh [QPM])
  cmmi-qpm-charts.py --json    # raw JSON dump (for downstream tools)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
STORE = REPO_ROOT / "projects" / "pycsl" / "docs" / "metrics" / "metrics-store.json"
REPORT_DIR = REPO_ROOT / "projects" / "pycsl" / "docs" / "reports"
SIGNAL_DIR = REPO_ROOT / "projects" / "pycsl" / "docs" / "audits"

# Thresholds
WEAK_MAX = 8       # < WEAK_MAX -> weak signal (no limits)
PRELIM_MAX = 20    # WEAK_MAX <= n < PRELIM_MAX -> preliminary; else stable
STALE_DAYS = 10    # warn if newest snapshot older than this


# ---------------------------------------------------------------------------
# KPI extractors (one per chart). Return list of (snapshot_idx, value).
# Skip snapshots where the KPI is missing or None (the chart tool
# tolerates gaps gracefully).
# ---------------------------------------------------------------------------

def _extract_global(snapshots: list[dict], dotted_key: str) -> list[tuple[int, float]]:
    out: list[tuple[int, float]] = []
    for i, s in enumerate(snapshots):
        v: Any = s.get("global", {})
        for part in dotted_key.split("."):
            v = v.get(part, None) if isinstance(v, dict) else None
            if v is None:
                break
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out.append((i, float(v)))
    return out


def _extract_per_system(
    snapshots: list[dict], sy_id: str, dotted_key: str
) -> list[tuple[int, float]]:
    out: list[tuple[int, float]] = []
    for i, s in enumerate(snapshots):
        sys_row = next(
            (x for x in s.get("systems", []) if x.get("id") == sy_id),
            None,
        )
        if not sys_row:
            continue
        v: Any = sys_row
        for part in dotted_key.split("."):
            v = v.get(part, None) if isinstance(v, dict) else None
            if v is None:
                break
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out.append((i, float(v)))
    return out


# ---------------------------------------------------------------------------
# Statistics + control limits
# ---------------------------------------------------------------------------

def _stats(values: list[float]) -> dict[str, float]:
    n = len(values)
    if n == 0:
        return {"n": 0, "mu": 0.0, "sigma": 0.0, "ucl": 0.0, "lcl": 0.0}
    mu = statistics.fmean(values)
    sigma = statistics.pstdev(values) if n > 1 else 0.0
    return {
        "n": n,
        "mu": mu,
        "sigma": sigma,
        "ucl": mu + 3 * sigma,
        "lcl": max(0.0, mu - 3 * sigma),
    }


# ---------------------------------------------------------------------------
# 4.1C — Western Electric rules
# ---------------------------------------------------------------------------

def _detect_signals(values: list[float], stats: dict[str, float]) -> list[dict]:
    """Return list of {rule, indices, description} for each WE-rule hit."""
    mu = stats["mu"]
    sigma = stats["sigma"]
    out: list[dict] = []
    if sigma == 0 or stats["n"] < 2:
        return out

    sigma1 = sigma
    sigma2 = 2 * sigma
    sigma3 = 3 * sigma

    # WE1: 1 point beyond ±3σ
    for i, v in enumerate(values):
        if v > mu + sigma3 or v < mu - sigma3:
            out.append({
                "rule": "WE1",
                "indices": [i],
                "description": f"point {i} (value {v:.3g}) is beyond ±3σ "
                               f"of μ={mu:.3g}",
            })

    # WE2: 2 of 3 consecutive points beyond ±2σ on same side
    if len(values) >= 3:
        for i in range(len(values) - 2):
            window = values[i:i + 3]
            above = sum(1 for v in window if v > mu + sigma2)
            below = sum(1 for v in window if v < mu - sigma2)
            if above >= 2:
                out.append({
                    "rule": "WE2",
                    "indices": list(range(i, i + 3)),
                    "description": f"≥2 of 3 points (indices {i}–{i + 2}) "
                                   f"are above μ+2σ ({mu + sigma2:.3g})",
                })
            if below >= 2:
                out.append({
                    "rule": "WE2",
                    "indices": list(range(i, i + 3)),
                    "description": f"≥2 of 3 points (indices {i}–{i + 2}) "
                                   f"are below μ−2σ ({mu - sigma2:.3g})",
                })

    # WE3: 4 of 5 consecutive points beyond ±1σ on same side
    if len(values) >= 5:
        for i in range(len(values) - 4):
            window = values[i:i + 5]
            above = sum(1 for v in window if v > mu + sigma1)
            below = sum(1 for v in window if v < mu - sigma1)
            if above >= 4:
                out.append({
                    "rule": "WE3",
                    "indices": list(range(i, i + 5)),
                    "description": f"≥4 of 5 points (indices {i}–{i + 4}) "
                                   f"are above μ+σ ({mu + sigma1:.3g})",
                })
            if below >= 4:
                out.append({
                    "rule": "WE3",
                    "indices": list(range(i, i + 5)),
                    "description": f"≥4 of 5 points (indices {i}–{i + 4}) "
                                   f"are below μ−σ ({mu - sigma1:.3g})",
                })

    # WE4: 8 consecutive points on same side of μ
    if len(values) >= 8:
        for i in range(len(values) - 7):
            window = values[i:i + 8]
            if all(v > mu for v in window):
                out.append({
                    "rule": "WE4",
                    "indices": list(range(i, i + 8)),
                    "description": f"8 consecutive points (indices {i}–{i + 7}) "
                                   f"all above μ ({mu:.3g})",
                })
            elif all(v < mu for v in window):
                out.append({
                    "rule": "WE4",
                    "indices": list(range(i, i + 8)),
                    "description": f"8 consecutive points (indices {i}–{i + 7}) "
                                   f"all below μ ({mu:.3g})",
                })
    return out


# ---------------------------------------------------------------------------
# Chart rendering
# ---------------------------------------------------------------------------

_SPARK = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return _SPARK[3] * len(values)
    width = len(_SPARK) - 1
    return "".join(
        _SPARK[int((v - lo) / (hi - lo) * width)] for v in values
    )


def _render_chart(
    title: str,
    series: list[tuple[int, float]],
    band_label: str,
) -> str:
    n = len(series)
    if n == 0:
        return (
            f"### {title}\n\n"
            f"_no data_ (KPI not yet observed in any snapshot)\n"
        )
    values = [v for _, v in series]
    stats = _stats(values)
    spark = _sparkline(values)
    signals = (
        _detect_signals(values, stats) if n >= WEAK_MAX else []
    )

    lines = [
        f"### {title}",
        "",
        f"**Signal:** {band_label} (n={n})",
        "",
        f"- Latest: `{values[-1]:.3g}`  "
        f"- Min: `{min(values):.3g}`  "
        f"- Max: `{max(values):.3g}`  "
        f"- μ: `{stats['mu']:.3g}`  "
        f"- σ: `{stats['sigma']:.3g}`",
    ]
    if n >= WEAK_MAX:
        lines.append(
            f"- UCL (μ+3σ): `{stats['ucl']:.3g}`  "
            f"LCL (max(0, μ−3σ)): `{stats['lcl']:.3g}`"
        )
    lines += [
        "",
        f"Series ({n} points): `{spark}`",
        "",
    ]
    if signals:
        lines.append(f"**Signals detected ({len(signals)}):**")
        lines.append("")
        for s in signals:
            lines.append(f"- **{s['rule']}** — {s['description']}")
        lines.append("")
    elif n >= WEAK_MAX:
        lines.append("_(no WE-rule violations)_\n")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def _band(n: int) -> str:
    if n < WEAK_MAX:
        return f"weak (n={n}, need ≥{WEAK_MAX} for limits)"
    if n < PRELIM_MAX:
        return f"preliminary (n={n}, need ≥{PRELIM_MAX} for stable)"
    return f"stable (n={n})"


def _systems_from_store(store: dict) -> list[tuple[str, str]]:
    latest = store.get("latest") or (
        store.get("snapshots", [{}])[-1] if store.get("snapshots") else {}
    )
    return [
        (sys["id"], sys["name"])
        for sys in latest.get("systems", [])
    ]


def build_report(store: dict, n_band_label: str, *, signals_only: bool = False) -> tuple[str, list[dict]]:
    """Return (markdown report text, list of all signals)."""
    snapshots = store.get("snapshots", [])
    if not snapshots and store.get("latest"):
        snapshots = [store["latest"]]
    n = len(snapshots)
    systems = _systems_from_store(store)

    ts = (
        _dt.datetime.now(_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    parts: list[str] = [
        "# CMMI QPM Report — PyCSL",
        "",
        f"**Generated:** {ts}",
        f"**Snapshots in store:** {n}",
        f"**Signal band:** {n_band_label}",
        f"**Source:** `{STORE.relative_to(REPO_ROOT)}`",
        "",
        "---",
        "",
        "## KPI 1 — Proof-success rate per system (per week, last 7 days)",
        "",
    ]
    all_signals: list[dict] = []

    for sy_id, sy_name in systems:
        series = _extract_per_system(
            snapshots, sy_id, "pycsl_proof_pass_rate_week.rate"
        )
        chart = _render_chart(
            f"{sy_id}-{sy_name}",
            series,
            _band(len(series)),
        )
        parts.append(chart)
        if len(series) >= WEAK_MAX:
            for s in _detect_signals([v for _, v in series], _stats([v for _, v in series])):
                s["kpi"] = "proof-success-rate"
                s["system"] = f"{sy_id}-{sy_name}"
                all_signals.append(s)

    parts += [
        "---",
        "",
        "## KPI 2 — Agent retry-count drift (coordinator, last 7 days avg)",
        "",
    ]
    series = _extract_global(snapshots, "coordinator_retries_week.avg")
    parts.append(_render_chart("Global retry avg", series, _band(len(series))))
    if len(series) >= WEAK_MAX:
        for s in _detect_signals([v for _, v in series], _stats([v for _, v in series])):
            s["kpi"] = "coordinator-retry-avg"
            s["system"] = "global"
            all_signals.append(s)

    parts += [
        "---",
        "",
        "## KPI 3 — L3-ceiling rate per system (cite:_note count snapshot)",
        "",
    ]
    for sy_id, sy_name in systems:
        series = _extract_per_system(snapshots, sy_id, "l3_ceiling_notes")
        chart = _render_chart(
            f"{sy_id}-{sy_name}",
            series,
            _band(len(series)),
        )
        parts.append(chart)
        if len(series) >= WEAK_MAX:
            for s in _detect_signals([v for _, v in series], _stats([v for _, v in series])):
                s["kpi"] = "l3-ceiling-notes"
                s["system"] = f"{sy_id}-{sy_name}"
                all_signals.append(s)

    parts += [
        "---",
        "",
        "## KPI 4 — Doc-coherency events / week (invocations)",
        "",
    ]
    series = _extract_global(snapshots, "doc_coherency_events_week.invocations")
    parts.append(_render_chart("Global invocations", series, _band(len(series))))
    if len(series) >= WEAK_MAX:
        for s in _detect_signals([v for _, v in series], _stats([v for _, v in series])):
            s["kpi"] = "doc-coherency-events"
            s["system"] = "global"
            all_signals.append(s)

    parts += [
        "---",
        "",
        "## Summary",
        "",
        f"- Snapshots: **{n}** ({_band(n)})",
        f"- WE-rule signals detected: **{len(all_signals)}**",
        "",
    ]
    if all_signals:
        parts.append("### Detected signals")
        parts.append("")
        for s in all_signals:
            parts.append(
                f"- **{s['rule']}** on `{s['kpi']}` / `{s['system']}` — {s['description']}"
            )
        parts.append("")
    parts.append(
        "_Per cmmi-tailoring-plan-follow-up-2.md Items 4.1B + 4.1C. "
        "Strong-signal flip happens automatically at snapshot 8._"
    )
    return "\n".join(parts), all_signals


def _next_report_path() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(REPORT_DIR.glob("qpm-report-*.md"))
    n = len(existing) + 1
    return REPORT_DIR / f"qpm-report-{n:03d}.md"


# ---------------------------------------------------------------------------
# 4.AT — band-transition detector + milestone marker
# ---------------------------------------------------------------------------
#
# When the band of the latest snapshot differs from the band of the
# previous snapshot (weak → preliminary, or preliminary → stable),
# emit a milestone marker at projects/pycsl/docs/audits/qpm-milestone-NNN.md.
# Idempotent: skip if a marker already exists with the same
# (prev_band, new_band, snapshot_count) tag.

def _band_name(n: int) -> str:
    """Return the bare band label (no countdown qualifier)."""
    if n < WEAK_MAX:
        return "weak"
    if n < PRELIM_MAX:
        return "preliminary"
    return "stable"


def _milestone_tag(prev_band: str, new_band: str, n: int) -> str:
    return f"qpm-milestone:{prev_band}->{new_band}:n={n}"


def _milestone_already_recorded(tag: str) -> bool:
    if not SIGNAL_DIR.is_dir():
        return False
    for existing in SIGNAL_DIR.glob("qpm-milestone-*.md"):
        try:
            head = existing.read_text()[:512]
        except OSError:
            continue
        if tag in head:
            return True
    return False


def _emit_milestone_if_transition(store: dict, report_path: Path) -> Optional[Path]:
    snapshots = store.get("snapshots", [])
    if len(snapshots) < 2:
        return None  # need at least 2 snapshots to detect a transition
    n_prev = len(snapshots) - 1
    n_curr = len(snapshots)
    prev_band = _band_name(n_prev)
    new_band = _band_name(n_curr)
    if prev_band == new_band:
        return None  # no transition
    tag = _milestone_tag(prev_band, new_band, n_curr)
    if _milestone_already_recorded(tag):
        return None
    SIGNAL_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(SIGNAL_DIR.glob("qpm-milestone-*.md"))
    nseq = len(existing) + 1
    out = SIGNAL_DIR / f"qpm-milestone-{nseq:03d}.md"
    ts = (
        _dt.datetime.now(_dt.timezone.utc)
        .replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    body = [
        f"# QPM Milestone #{nseq:03d} — band transition",
        "",
        f"**Tag:** `{tag}`",
        f"**Generated:** {ts}",
        f"**Report:** [`{report_path.name}`](../reports/{report_path.name})",
        "",
        f"The metrics store crossed a signal-band boundary:",
        "",
        f"- Previous band: **{prev_band}** (n={n_prev})",
        f"- New band: **{new_band}** (n={n_curr})",
        "",
        "## What this means",
        "",
    ]
    explanations = {
        "weak->preliminary": (
            "Enough snapshots ({n}) have accumulated for `bin/cmmi-qpm-charts.py` "
            "to compute control limits (UCL = μ+3σ, LCL = max(0, μ−3σ)). The "
            "Western Electric rule detector is now active. Treat the limits as "
            "**preliminary** — they will tighten as more snapshots accumulate.\n"
            "\n"
            "Per Item 4.AUTO of `cmmi-tailoring-plan-follow-up-3.md`."
        ),
        "preliminary->stable": (
            "The KPI series has reached {n} snapshots, which is the threshold "
            "above which baselines are treated as **stable**. Control limits, "
            "WE-rule signals, and any QPM signal escalations now carry full "
            "evidentiary weight under `cmmi-glue` Workflow 3."
        ),
        "weak->stable": (
            "Unusual transition: snapshot count jumped from <{weak} to ≥{prelim} "
            "in a single ingest. Verify this is intentional (e.g., a one-shot "
            "bulk import) rather than a metrics-store edit."
        ),
    }
    key = f"{prev_band}->{new_band}"
    explanation = explanations.get(
        key, "Band transition observed; no canned explanation available."
    ).format(n=n_curr, weak=WEAK_MAX, prelim=PRELIM_MAX)
    body.append(explanation)
    body.append("")
    body.append("## Next steps")
    body.append("")
    if new_band == "preliminary":
        body.append(
            "- Review the QPM report's per-KPI tables; the μ/σ/UCL/LCL "
            "values are now meaningful."
        )
        body.append(
            "- Watch the next few snapshots for any WE-rule signal escalations "
            "(`projects/pycsl/docs/audits/qpm-signal-*.md`)."
        )
    elif new_band == "stable":
        body.append(
            "- Baselines are now stable enough to publish externally or "
            "consume in downstream decisions (e.g., feature-plan prioritisation)."
        )
        body.append(
            "- Future signals carry full Workflow-3 escalation weight."
        )
    body.append("")
    out.write_text("\n".join(body))
    return out


def _stale_warn(store: dict) -> Optional[str]:
    latest = store.get("latest")
    if not latest:
        return "no snapshots yet"
    ts_raw = latest.get("timestamp")
    if not ts_raw:
        return None
    try:
        ts = _dt.datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    age = _dt.datetime.now(_dt.timezone.utc) - ts
    if age.days >= STALE_DAYS:
        return f"newest snapshot is {age.days} days old (≥{STALE_DAYS})"
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true",
                   help="Informational summary only; always exit 0. "
                   "Called from bin/cmmi-audit.sh [QPM].")
    g.add_argument("--json", action="store_true",
                   help="Print JSON dump of all signals + counts; exit 0.")
    args = ap.parse_args(argv)

    if not STORE.is_file():
        print(f"cmmi-qpm-charts: no metrics store at "
              f"{STORE.relative_to(REPO_ROOT)} — run "
              f"bin/cmmi-metrics-ingest.py --weekly first",
              file=sys.stderr)
        return 1 if not args.check else 0
    store = json.loads(STORE.read_text())
    snapshots = store.get("snapshots", [])
    n = len(snapshots)
    band_label = _band(n)
    stale = _stale_warn(store)

    if args.check:
        # Audit-mode: informational summary, exit 0 always.
        print(f"cmmi-qpm-charts --check  snapshots={n}  band={band_label}")
        # 4.AUDc — countdown line (one line, parsed nowhere — pure UX)
        if n < WEAK_MAX:
            need = WEAK_MAX - n
            print(f"  countdown: snapshot {n} of {WEAK_MAX} "
                  f"for preliminary mode (~{need * 7} days at weekly cadence)")
        elif n < PRELIM_MAX:
            need = PRELIM_MAX - n
            print(f"  countdown: snapshot {n} of {PRELIM_MAX} "
                  f"for stable mode (~{need * 7} days at weekly cadence)")
        else:
            print(f"  countdown: stable (n={n} ≥ {PRELIM_MAX})")
        if stale:
            print(f"  warning: {stale}")
        # Run report in-memory to count signals
        _, signals = build_report(store, band_label)
        print(f"  WE-rule signals: {len(signals)}")
        for s in signals[:5]:
            print(f"    - {s['rule']} on {s['kpi']}/{s.get('system')}")
        return 0

    if args.json:
        _, signals = build_report(store, band_label)
        print(json.dumps({
            "snapshots": n,
            "band": band_label,
            "stale": stale,
            "signals": signals,
        }, indent=2))
        return 0

    # Default: emit a fresh report
    text, signals = build_report(store, band_label)
    out = _next_report_path()
    out.write_text(text)
    print(f"cmmi-qpm-charts: wrote {out.relative_to(REPO_ROOT)} "
          f"(snapshots={n}, signals={len(signals)})")
    if stale:
        print(f"  warning: {stale}")

    # 4.AT — emit milestone marker on band transition (idempotent)
    milestone = _emit_milestone_if_transition(store, out)
    if milestone:
        print(f"  band transition -> {milestone.relative_to(REPO_ROOT)}")

    # WE-rule signals get a separate audit entry per cmmi-glue
    # Workflow 3 (signal escalation).
    if signals:
        SIGNAL_DIR.mkdir(parents=True, exist_ok=True)
        existing = sorted(SIGNAL_DIR.glob("qpm-signal-*.md"))
        n2 = len(existing) + 1
        sig_path = SIGNAL_DIR / f"qpm-signal-{n2:03d}.md"
        ts_now = (
            _dt.datetime.now(_dt.timezone.utc)
            .replace(microsecond=0).isoformat().replace("+00:00", "Z")
        )
        body = [
            f"# QPM Signal Escalation #{n2:03d}",
            "",
            f"**Generated:** {ts_now}",
            f"**Report:** [`{out.name}`](../reports/{out.name})",
            "",
            f"{len(signals)} Western Electric rule(s) triggered:",
            "",
        ]
        for s in signals:
            body.append(
                f"- **{s['rule']}** on `{s['kpi']}` / `{s.get('system')}` — "
                f"{s['description']}"
            )
        body.append("")
        body.append(
            "Per `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance "
            "Escalation), the developer reviews and decides whether to "
            "investigate the underlying KPI drift."
        )
        sig_path.write_text("\n".join(body))
        print(f"  signal escalation -> {sig_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
