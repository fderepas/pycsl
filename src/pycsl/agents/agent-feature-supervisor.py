#!/usr/bin/env python3
"""agent-feature-supervisor — orchestrate the rollout of an approved
missing-*-feature.md plan.

Per better-agent.md Phase 3 and cmmi-tailoring-plan-follow-up.md
Item 1.3. **v1: gate-only.** The supervisor never writes code itself.
It does three things:

  1. Parse the feature plan's "Implementation surface" section into
     a list of phases, each phase with a list of target files.
  2. For each phase, check the targets against the load-bearing
     deny-list (config/skills/agent-stdlib-annotate/references/
     load-bearing-files.md). If any target matches the deny-list,
     halt with exit 75 (human-needed) and write a halt-report.
  3. Otherwise, run the verification gate (pytest, reference tests,
     doc-coherency, cmmi-audit, stdlib-coverage diff). Halt with
     exit 74 on first gate failure.

Exit codes (extend coordinator.py's 72/73 convention):
  0   all phases either passed the gate or finished without action.
  72  inherited from coordinator (max retries) — not used by v1.
  73  inherited from coordinator (loop detection) — not used by v1.
  74  phase gate failure (pytest, doc-coherency, etc.).
  75  human-needed signal raised (load-bearing file modification).
  76  rollback failure (per-phase git-tag restore failed) — v1 stub.

Usage:
    bin/agent-feature-supervisor --feature-file <path.md>
    bin/agent-feature-supervisor --feature-file <path.md> --skip-gate
        (parse + classify only; useful for dry runs and tests)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent

# Mirror agent-stdlib-annotate.py's pattern: re-use the shared LLM
# client log() helper (we do not use llm_generate in v1 — supervisor
# is gate-only, no LLM calls).
sys.path.insert(0, str(_PROJECT_ROOT / "src" / "pycsl" / "agents"))
from llm_client import log  # noqa: E402

AGENT_NAME = "agent-feature-supervisor"

# Exit-code convention extends coordinator.py:
EXIT_OK = 0
EXIT_GATE_FAIL = 74
EXIT_HUMAN_NEEDED = 75
EXIT_ROLLBACK_FAIL = 76

_LOAD_BEARING_FILE = (
    _PROJECT_ROOT
    / "config"
    / "skills"
    / "agent-stdlib-annotate"
    / "references"
    / "load-bearing-files.md"
)

_HALT_REPORT_ROOT = _PROJECT_ROOT / "metrics" / "feature-supervisor"
_BRIDGE_CURSOR = _PROJECT_ROOT / "projects" / "pycsl" / "message-queues" / ".bridge-cursor.json"
_METRICS_LOGS = _PROJECT_ROOT / "metrics" / "logs"

_CODING_LLM_PROMPT = (
    _PROJECT_ROOT
    / "config"
    / "skills"
    / "agent-stdlib-annotate"
    / "references"
    / "coding-llm-prompt.md"
)


# ---------------------------------------------------------------------------
# Load-bearing deny-list
# ---------------------------------------------------------------------------

def load_deny_list() -> List[str]:
    """Parse the deny-list from the load-bearing-files.md fenced block."""
    if not _LOAD_BEARING_FILE.is_file():
        return []
    text = _LOAD_BEARING_FILE.read_text()
    # First triple-backtick fence block contains the deny-list paths
    m = re.search(r"```\n(.*?)\n```", text, re.S)
    if not m:
        return []
    return [
        line.strip()
        for line in m.group(1).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def is_load_bearing(target: str, deny_list: List[str]) -> Optional[str]:
    """Return the matched deny-list entry if `target` is load-bearing."""
    # Normalise: a feature plan may quote paths with backticks, leading
    # slashes, or repo-relative form. Strip noise.
    cleaned = target.strip().strip("`").lstrip("./").lstrip("/")
    for entry in deny_list:
        e = entry.strip()
        if not e:
            continue
        # Directory entry (ends with /): match if target is under it
        if e.endswith("/"):
            if cleaned.startswith(e) or cleaned == e.rstrip("/"):
                return e
        # File entry: match if target ends with it
        elif cleaned.endswith(e) or cleaned == e:
            return e
    return None


# ---------------------------------------------------------------------------
# Feature-plan parser
# ---------------------------------------------------------------------------

@dataclass
class Phase:
    number: int
    title: str
    target_files: List[str] = field(default_factory=list)
    raw_body: str = ""


_PHASE_HEADER_RE = re.compile(
    r"^###\s+Phase\s+(\d+)\s*(?:\.\d+)?\s*(?:—|-|:|\b)?\s*(.*?)\s*$",
    re.M,
)

# File references inside phase tables — match `path/like/this.py`
# (with or without backticks). We accept paths that contain a `/`
# or end in a recognised extension to avoid matching English words.
_PATH_RE = re.compile(
    r"`([^`\n]+?\.[A-Za-z0-9]+|[^`\n]+?/[^`\n]+?)`"
)


def parse_feature_plan(text: str) -> List[Phase]:
    """Extract the phase list from a missing-*-feature.md document."""
    # Restrict to the "Implementation surface" section if present —
    # phases outside that section are not orchestrated targets.
    section_match = re.search(
        r"^##\s+Implementation surface\b(.*?)(?=^##\s+(?!#))",
        text, re.S | re.M,
    )
    body = section_match.group(1) if section_match else text

    headers = list(_PHASE_HEADER_RE.finditer(body))
    phases: List[Phase] = []
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        phase_body = body[start:end]
        targets = []
        seen = set()
        for pm in _PATH_RE.finditer(phase_body):
            p = pm.group(1).strip()
            # Filter obvious non-files (URLs, version refs, etc.)
            if p.startswith(("http://", "https://", "git@")):
                continue
            if p in seen:
                continue
            seen.add(p)
            targets.append(p)
        phases.append(Phase(
            number=int(m.group(1)),
            title=m.group(2).strip(),
            target_files=targets,
            raw_body=phase_body.strip(),
        ))
    return phases


# ---------------------------------------------------------------------------
# Verification gate
# ---------------------------------------------------------------------------

@dataclass
class GateStep:
    name: str
    cmd: List[str]
    skip_if_missing: bool = False  # if the tool doesn't exist, skip with PASS


GATE_STEPS: List[GateStep] = [
    GateStep("pytest tests/",
             ["pytest", "-q", "tests/"], skip_if_missing=True),
    GateStep("bin/run-reference-tests.sh",
             [str(_PROJECT_ROOT / "bin" / "run-reference-tests.sh")],
             skip_if_missing=True),
    GateStep("bin/doc-coherency.py --check",
             [str(_PROJECT_ROOT / "bin" / "doc-coherency.py"), "--check"]),
    GateStep("bin/cmmi-audit.sh",
             [str(_PROJECT_ROOT / "bin" / "cmmi-audit.sh"), "--quick"]),
    GateStep("bin/stdlib-coverage-report.py",
             [str(_PROJECT_ROOT / "bin" / "stdlib-coverage-report.py")],
             skip_if_missing=True),
]


@dataclass
class GateResult:
    step: str
    passed: bool
    skipped: bool
    output: str


def run_gate() -> List[GateResult]:
    results: List[GateResult] = []
    for step in GATE_STEPS:
        if step.skip_if_missing and not Path(step.cmd[0]).exists():
            results.append(GateResult(step.name, True, True, ""))
            continue
        try:
            r = subprocess.run(
                step.cmd,
                cwd=str(_PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=600,
            )
            results.append(GateResult(
                step.name,
                r.returncode == 0,
                False,
                (r.stdout + r.stderr)[-2000:],
            ))
            if r.returncode != 0:
                break  # halt on first failure
        except FileNotFoundError:
            results.append(GateResult(step.name, True, True, ""))
        except subprocess.TimeoutExpired:
            results.append(GateResult(step.name, False, False,
                                      "TIMEOUT (>10 min)"))
            break
    return results


# ---------------------------------------------------------------------------
# Halt-report writer
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1.4a + 1.4b — coding-LLM delegation (off by default)
# ---------------------------------------------------------------------------

def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run git with strict args (never inject user-controlled paths
    without `--` separator). NEVER use --hard, -f, force-push, etc."""
    forbidden = {"--hard", "-f", "--force", "push", "commit",
                 "rebase", "clean"}
    for a in args:
        if a in forbidden:
            raise RuntimeError(
                f"_git: refusing forbidden arg {a!r} — supervisor "
                f"safety perimeter (1.4b)"
            )
    r = subprocess.run(
        ["git", *args],
        cwd=str(_PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if check and r.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} -> exit {r.returncode}\n"
            f"stderr: {r.stderr}"
        )
    return r


def _phase_tag(slug: str, phase_number: int) -> str:
    return f"feature-{slug}-phase-{phase_number}-start"


def _build_phase_prompt(phase: "Phase", plan_text: str) -> str:
    """Wrap the coding-LLM scaffold around the phase body + target file contents."""
    if not _CODING_LLM_PROMPT.is_file():
        scaffold = "(coding-llm-prompt.md missing; falling back to bare instructions)"
    else:
        scaffold = _CODING_LLM_PROMPT.read_text()

    parts = [
        scaffold,
        "",
        "---",
        "",
        f"## This phase: Phase {phase.number} — {phase.title}",
        "",
        "### Phase body (from the feature plan)",
        "",
        phase.raw_body,
        "",
        "### Target files (current contents)",
        "",
    ]
    for target in phase.target_files:
        p = _PROJECT_ROOT / target.lstrip("./").lstrip("/")
        if p.is_file():
            try:
                content = p.read_text()
            except UnicodeDecodeError:
                content = "(binary file; not inlined)"
        elif p.is_dir():
            content = "(directory target; list its contents in your diff)"
        else:
            content = "(file does not yet exist; create it in your diff)"
        parts.append(f"#### `{target}`")
        parts.append("")
        parts.append("```")
        parts.append(content)
        parts.append("```")
        parts.append("")
    return "\n".join(parts)


_DIFF_FENCE_RE = re.compile(
    r"```(?:diff)?\s*\n(.*?)\n```", re.S | re.I
)


def _extract_diff(llm_output: str) -> Optional[str]:
    """Find the first fenced diff block. None if absent."""
    m = _DIFF_FENCE_RE.search(llm_output)
    if not m:
        return None
    body = m.group(1)
    # Trim a leading `# refuse:` comment marker — treat as no diff.
    if body.strip().startswith("# refuse:"):
        return None
    return body


def _apply_diff(diff_text: str) -> tuple[bool, str]:
    """Validate + apply a unified diff. Returns (success, stderr-text)."""
    # First validate with --check so we don't mutate the tree on garbage
    r = subprocess.run(
        ["git", "apply", "--check", "--whitespace=nowarn", "--recount", "-"],
        cwd=str(_PROJECT_ROOT),
        input=diff_text,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return False, f"git apply --check failed:\n{r.stderr}"
    # Apply for real
    r = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "--recount", "-"],
        cwd=str(_PROJECT_ROOT),
        input=diff_text,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return False, f"git apply failed:\n{r.stderr}"
    return True, ""


def _rollback_phase(slug: str, phase_number: int,
                    target_files: list[str]) -> bool:
    """Revert per-phase targets to the per-phase start tag. Returns success."""
    tag = _phase_tag(slug, phase_number)
    # Check tag exists
    r = _git("rev-parse", "--verify", tag, check=False)
    if r.returncode != 0:
        return False
    # Restore each target (--worktree + --staged)
    for target in target_files:
        try:
            _git("restore", f"--source={tag}", "--worktree", "--staged",
                 "--", target)
        except RuntimeError:
            return False
    # Delete the tag (rollback complete)
    _git("tag", "-d", tag, check=False)
    return True


def _delegate_phase(phase: "Phase", plan_text: str,
                    slug: str) -> tuple[bool, str]:
    """Run coding-LLM delegation for one phase. Returns (success, message).

    Behaviour:
        1. Tag HEAD as feature-<slug>-phase-<N>-start.
        2. Build phase-scoped prompt, dispatch via llm_generate.
        3. Extract fenced diff. If absent (LLM refused or malformed),
           return (False, "llm-refused").
        4. git apply --check then git apply.
        5. Run verification gate (subset).
        6. On gate fail: _rollback_phase and return (False, "gate-fail").
        7. On success: KEEP the tag (audit trail) and return (True, "").
    """
    # Best-effort import of llm_generate; defer error until needed
    try:
        from llm_client import llm_generate  # type: ignore
    except ImportError as e:
        return False, f"llm_client unavailable: {e}"

    tag = _phase_tag(slug, phase.number)
    # Create the start tag at HEAD; allow overwrite via -f (the only
    # -f we allow, scoped to tags only; bypass _git's check).
    subprocess.run(["git", "tag", "-f", tag],
                   cwd=str(_PROJECT_ROOT),
                   capture_output=True)

    prompt = _build_phase_prompt(phase, plan_text)
    try:
        llm_output = llm_generate(
            prompt=prompt,
            system="You are a coding assistant. Follow the rules in "
                   "the coding-llm-prompt scaffold above. Output a "
                   "unified diff in a fenced ```diff block.",
            agent_id=AGENT_NAME,
            model=os.environ.get("PYCSL_LLM_MODEL", ""),
        )
    except Exception as e:
        return False, f"llm_generate raised: {e}"

    diff = _extract_diff(llm_output)
    if not diff:
        return False, "llm refused or output had no diff block"

    ok, err = _apply_diff(diff)
    if not ok:
        return False, err

    # Re-run the gate (subset — just the cheap steps)
    quick_results = run_gate()
    if not all(r.passed for r in quick_results):
        _rollback_phase(slug, phase.number, phase.target_files)
        return False, "gate-fail (rolled back)"

    return True, ""


# ---------------------------------------------------------------------------
# Item 3.4 — agent log-context reader (queue-first, log-fallback)
# ---------------------------------------------------------------------------
#
# Backwards-compatible reader used by future log-citing features
# (e.g., LLM delegation prompts that quote recent agent activity,
# halt-reports that include relevant log lines). NOT YET CALLED by
# any existing code — pure forward-looking infrastructure landed
# today so that Item 3.4r (fallback removal) becomes a 1-line edit
# after the 14-day bridge clock plus a successful 1.4 delegation
# elapses (per cmmi-tailoring-plan-follow-up-3.md).
#
# Order of precedence:
#   1. Queue (projects/pycsl/message-queues/<agent>/inbox-from-logs/) —
#      canonical source once the bridge has run.
#   2. metrics/logs/<agent>.log — fallback when the queue is empty
#      AND the bridge cursor doesn't exist (fresh checkout, or
#      bridge has never run).
#
# Returns line text only (strings); callers that need the structured
# message envelope can call queue_reader.iter_messages() directly.

def _read_agent_log_context(
    agent: str,
    *,
    since: Optional["datetime.datetime"] = None,
    max_messages: int = 100,
) -> List[str]:
    """Return up to `max_messages` log lines for `agent`, queue-first.

    Item 3.4 scaffolding: no callers yet. The signature is the
    target API that future features (1.4-era LLM prompts,
    halt-report enrichment) will call.
    """
    # Try queue first
    queue_lines: List[str] = []
    try:
        import queue_reader  # type: ignore
        for msg in queue_reader.iter_messages(agent, since=since):
            queue_lines.append(msg.get("line_text", ""))
            if len(queue_lines) >= max_messages:
                break
    except ImportError:
        # queue_reader missing means we're in a degraded environment;
        # fall through to log-only mode.
        pass

    if queue_lines:
        return queue_lines

    # Fallback to metrics/logs/<agent>.log — only when the bridge
    # has never run (cursor absent). If the bridge HAS run and the
    # queue is empty, the agent legitimately has no recent activity;
    # do NOT fall back (that would mask bridge breakage).
    if _BRIDGE_CURSOR.is_file():
        return []

    log_file = _METRICS_LOGS / f"{agent}.log"
    if not log_file.is_file():
        return []
    try:
        lines = log_file.read_text(errors="replace").splitlines()
    except OSError:
        return []
    # Take last `max_messages` non-blank lines (most-recent activity)
    non_blank = [ln for ln in lines if ln.strip()]
    return non_blank[-max_messages:]


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()[:64]


def write_halt_report(
    feature_file: Path,
    phases: List[Phase],
    deny_hits: List[Tuple[int, str, str]],
    gate_results: List[GateResult],
    exit_reason: str,
) -> Path:
    slug = _slug(feature_file.stem)
    report_dir = _HALT_REPORT_ROOT / slug
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / "halt-report.md"
    ts = (
        datetime.datetime.now(datetime.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    lines: List[str] = [
        f"# agent-feature-supervisor halt report — {slug}",
        "",
        f"**Generated:** {ts}",
        f"**Feature file:** `{feature_file}`",
        f"**Reason:** {exit_reason}",
        "",
        "## Parsed phases",
        "",
    ]
    for p in phases:
        lines.append(f"### Phase {p.number} — {p.title}")
        lines.append("")
        lines.append(f"**Target files ({len(p.target_files)}):**")
        for t in p.target_files:
            tag = ""
            for ph_num, target, matched in deny_hits:
                if ph_num == p.number and target == t:
                    tag = f"  ← **LOAD-BEARING** (matches `{matched}`)"
                    break
            lines.append(f"- `{t}`{tag}")
        lines.append("")

    if deny_hits:
        lines += [
            "## Load-bearing deny-list hits",
            "",
            "These target files appear in the deny-list at "
            "`config/skills/agent-stdlib-annotate/references/load-bearing-files.md`. "
            "Per the safety perimeter (better-agent.md §Safety perimeter), the "
            "supervisor halts and requires human review before any edit attempt.",
            "",
        ]
        for ph_num, target, matched in deny_hits:
            lines.append(
                f"- Phase {ph_num}: `{target}` matches deny-list entry `{matched}`"
            )
        lines.append("")

    if gate_results:
        lines += ["## Verification gate", ""]
        for r in gate_results:
            mark = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
            lines.append(f"- [{mark}] {r.step}")
            if not r.passed and not r.skipped:
                lines.append("")
                lines.append("  ```")
                for ln in r.output.splitlines()[-10:]:
                    lines.append(f"  {ln}")
                lines.append("  ```")
        lines.append("")

    lines += [
        "## Next steps",
        "",
        "1. Human reviews the deny-list hits and decides whether to "
        "proceed with manual edits or to reject the plan.",
        "2. After manual edits, re-run `bin/cmmi-audit.sh` to confirm "
        "the gate is green.",
        "3. If the plan needs revision, edit the feature file and "
        "re-invoke `bin/agent-feature-supervisor --feature-file <path>`.",
        "",
    ]
    out.write_text("\n".join(lines))
    return out


# ---------------------------------------------------------------------------
# Main loop (v1 — gate-only)
# ---------------------------------------------------------------------------

def supervise(feature_file: Path, skip_gate: bool,
              allow_llm_delegation: bool = False) -> int:
    if not feature_file.is_file():
        print(f"[{AGENT_NAME}] error: feature file does not exist: "
              f"{feature_file}", file=sys.stderr)
        return 2
    text = feature_file.read_text()
    phases = parse_feature_plan(text)
    if not phases:
        print(f"[{AGENT_NAME}] error: no '### Phase N' headers found under "
              f"'## Implementation surface' in {feature_file}", file=sys.stderr)
        return 2

    deny_list = load_deny_list()
    deny_hits: List[Tuple[int, str, str]] = []
    for p in phases:
        for t in p.target_files:
            matched = is_load_bearing(t, deny_list)
            if matched:
                deny_hits.append((p.number, t, matched))

    print(f"[{AGENT_NAME}] parsed {len(phases)} phases from {feature_file.name}")
    for p in phases:
        print(f"  Phase {p.number}: {p.title} — {len(p.target_files)} target file(s)")
    print(f"[{AGENT_NAME}] deny-list entries: {len(deny_list)}; "
          f"load-bearing hits: {len(deny_hits)}")

    gate_results: List[GateResult] = []

    # 1.4a — LLM delegation (off by default). Only invoked when the
    # flag is set AND there are no deny-list hits AND there are
    # phases that have target files.
    delegation_results: list[tuple[int, bool, str]] = []
    if allow_llm_delegation and not deny_hits:
        slug = _slug(feature_file.stem)
        delegate_phases = [p for p in phases if p.target_files]
        if not delegate_phases:
            print(f"[{AGENT_NAME}] --allow-llm-delegation: no phases "
                  f"with target files to delegate.")
        else:
            print(f"[{AGENT_NAME}] --allow-llm-delegation: delegating "
                  f"{len(delegate_phases)} phases (LLM-driven; per-phase "
                  f"git-tag rollback on gate failure).")
            for p in delegate_phases:
                ok, msg = _delegate_phase(p, text, slug)
                delegation_results.append((p.number, ok, msg))
                status = "OK" if ok else "FAIL"
                print(f"  Phase {p.number} {status}: {msg or 'delegated diff applied + gate green'}")
                if not ok:
                    break  # halt on first failure
    elif not skip_gate and not deny_hits:
        print(f"[{AGENT_NAME}] running verification gate ...")
        gate_results = run_gate()
        for r in gate_results:
            mark = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
            print(f"  [{mark}] {r.step}")

    # Decide exit
    if deny_hits:
        reason = (
            f"Human-needed: {len(deny_hits)} load-bearing file(s) named in "
            f"feature-plan phases. Supervisor (v1, gate-only) does not "
            f"edit load-bearing files autonomously."
        )
        out = write_halt_report(feature_file, phases, deny_hits, gate_results, reason)
        print(f"[{AGENT_NAME}] halt-report -> {out.relative_to(_PROJECT_ROOT)}")
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=75 feature={feature_file.name} "
            f"deny_hits={len(deny_hits)}")
        return EXIT_HUMAN_NEEDED

    if gate_results and not all(r.passed for r in gate_results):
        reason = "Gate failure: one or more verification steps failed."
        out = write_halt_report(feature_file, phases, deny_hits, gate_results, reason)
        print(f"[{AGENT_NAME}] halt-report -> {out.relative_to(_PROJECT_ROOT)}")
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=74 feature={feature_file.name} gate_fail")
        return EXIT_GATE_FAIL

    # 1.4a delegation result handling
    if delegation_results and not all(ok for (_, ok, _) in delegation_results):
        failed = [(n, m) for (n, ok, m) in delegation_results if not ok]
        reason = (
            f"Delegated phase(s) failed: {failed[0][0]} ({failed[0][1]}). "
            f"Tree restored via per-phase tag."
        )
        out = write_halt_report(feature_file, phases, deny_hits, [], reason)
        print(f"[{AGENT_NAME}] halt-report -> {out.relative_to(_PROJECT_ROOT)}")
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=74 feature={feature_file.name} delegation_fail")
        return EXIT_GATE_FAIL

    # v1 success: no deny-list hits AND (gate skipped OR gate green).
    # The supervisor doesn't claim to have IMPLEMENTED anything — it
    # claims that no load-bearing files would be touched and the gate
    # is currently green. The actual implementation is the human's job
    # under v1.
    print(f"[{AGENT_NAME}] OK — no load-bearing hits; gate green. "
          f"Human implements phases manually; supervisor verifies after.")
    log(str(_PROJECT_ROOT), AGENT_NAME,
        f"OK feature={feature_file.name} phases={len(phases)}")
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature-rollout supervisor.")
    parser.add_argument("--feature-file", type=Path, required=True,
                        help="Path to an approved missing-*-feature.md plan.")
    parser.add_argument("--skip-gate", action="store_true",
                        help="Skip the verification gate (parse + "
                        "deny-list check only).")
    parser.add_argument("--allow-llm-delegation", action="store_true",
                        help="Item 1.4a: delegate non-load-bearing phases "
                        "to a coding LLM. Per-phase git-tag rollback on "
                        "gate failure. Default OFF (preserves gate-only "
                        "v1 behaviour).")
    args = parser.parse_args()
    return supervise(args.feature_file, args.skip_gate,
                     allow_llm_delegation=args.allow_llm_delegation)


if __name__ == "__main__":
    sys.exit(main())
