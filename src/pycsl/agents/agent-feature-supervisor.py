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

The supervisor's persona and Extreme Rigor discipline are documented in
``config/agents/agent-feature-supervisor.md`` (loaded as ``_AGENT_DESCRIPTION``
and prepended to LLM-delegation prompts so a delegate inherits the same
rules). The acceptance-block syntax authors write against lives in
``config/skills/csl-from-scratch/references/acceptance-syntax.md``.

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

# ER halt reason codes (all map to exit 75 — human-needed).
# Reported in halt-report header and run-log so the failure mode is
# unambiguous.
REASON_MISSING_ACCEPTANCE = "MISSING_ACCEPTANCE"
REASON_STATUS_FORGED = "STATUS_FORGED"
REASON_ACCEPTANCE_FAILED = "ACCEPTANCE_FAILED"
REASON_CLAIM_REJECTED = "CLAIM_REJECTED"

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

# The supervisor's own persona / ER discipline. Loaded into LLM
# delegation prompts so a delegate operates under the same Extreme
# Rigor rules this module enforces. (Gap 11 of the post-implementation
# retrospective: the persona doc existed but nothing read it.)
_AGENT_DESCRIPTION = (
    _PROJECT_ROOT
    / "config"
    / "agents"
    / "agent-feature-supervisor.md"
)

# Competency matrix (skill-to-role) — which skills each level needs, read by
# the resolver to inject role-appropriate skills into delegate prompts and to
# log the resolution in the harness-structure record's `## 5` section.
_SKILLS_ROOT = _PROJECT_ROOT / "config" / "skills"
_COMPETENCY_FILE = (
    _SKILLS_ROOT / "project-lifecycle" / "references" / "competency-matrix.md"
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

# ---- Extreme Rigor: acceptance claims ----------------------------------
#
# Per feature-supervisor-extreme-rigor.md: every non-DONE phase carries an
# `**Acceptance:**` block whose bullets the supervisor executes. Each bullet
# is `\`command\` <predicate>` where predicate is one of:
#   `exits N`                        — exit code == N (default 0)
#   `stdout == \`value\``            — stdout (stripped) == value
#   `stdout >= \`N\``                — stdout (parsed as int) >= N
#   `stdout matches \`regex\``       — re.search(regex, stdout) hits
#
# A phase may carry `**Acceptance:** none — <reason>` to opt out
# explicitly (research/docs-only phases).

@dataclass
class Predicate:
    """Base class for acceptance predicates."""
    kind: str
    def describe(self) -> str:  # human-readable label for halt-report
        return self.kind

@dataclass
class ExitsN(Predicate):
    n: int = 0
    def __post_init__(self): self.kind = "exits"
    def describe(self) -> str: return f"exits {self.n}"

@dataclass
class StdoutEq(Predicate):
    value: str = ""
    def __post_init__(self): self.kind = "stdout=="
    def describe(self) -> str: return f"stdout == {self.value!r}"

@dataclass
class StdoutGe(Predicate):
    threshold: int = 0
    def __post_init__(self): self.kind = "stdout>="
    def describe(self) -> str: return f"stdout >= {self.threshold}"

@dataclass
class StdoutMatches(Predicate):
    regex: str = ""
    def __post_init__(self): self.kind = "stdout-matches"
    def describe(self) -> str: return f"stdout matches /{self.regex}/"

@dataclass
class AcceptanceClaim:
    command: str
    predicate: Predicate
    raw_line: str   # full bullet text for halt-report quoting

@dataclass
class AcceptanceResult:
    claim: AcceptanceClaim
    passed: bool
    stdout_excerpt: str = ""
    reason_if_failed: str = ""


# Parser regex for an acceptance bullet. Allows arbitrary trailing
# italic-paren comments like `*(no matches)*`.
_ACCEPTANCE_BULLET_RE = re.compile(
    r"""
    ^\s*-\s*                          # bullet marker
    `(?P<cmd>[^`]+)`                  # the command in backticks
    \s+
    (?:                               # predicate alternatives:
        exits\s+(?P<exits>\d+)
      | stdout\s*==\s*`(?P<eq>[^`]*)`
      | stdout\s*>=\s*`(?P<ge>\d+)`
      | stdout\s+matches\s*`(?P<match>[^`]+)`
    )
    \s*
    (?:\*\(.*?\)\*)?                  # optional italic comment
    \s*$
    """,
    re.VERBOSE,
)

# `**Acceptance:** none — <reason>` opt-out
_ACCEPTANCE_NONE_RE = re.compile(
    r"^\*\*Acceptance:\*\*\s*none\s*(?:[-—]+\s*(.+))?$",
    re.M,
)

# `**Acceptance:**` block header (without `none`)
_ACCEPTANCE_HEADER_RE = re.compile(
    r"^\*\*Acceptance:\*\*\s*$",
    re.M,
)


def _parse_acceptance(phase_body: str) -> List[AcceptanceClaim]:
    """Extract `**Acceptance:**` bullets from a phase body.

    Returns [] if no Acceptance block is present, or if the block is
    explicitly `none — <reason>` (caller distinguishes these via
    `_acceptance_optout_reason`).

    Bullets that don't match the expected shape are silently dropped
    — but `_validate_plan_completeness` will flag a non-empty
    Acceptance header whose bullets all dropped, treating the phase
    as effectively claim-less.
    """
    none_match = _ACCEPTANCE_NONE_RE.search(phase_body)
    if none_match:
        return []
    header_match = _ACCEPTANCE_HEADER_RE.search(phase_body)
    if not header_match:
        return []
    # Body of the Acceptance block is from end-of-header to either the
    # next blank-line-then-non-bullet, or end of phase body.
    start = header_match.end()
    block = phase_body[start:]
    # Stop at first blank line followed by non-bullet content (often
    # the next sub-heading or paragraph).
    lines = block.split("\n")
    claims: List[AcceptanceClaim] = []
    for line in lines:
        if not line.strip():
            # Blank line ends the block iff next line isn't a bullet
            # — but since we iterate all lines and skip blanks, we
            # rely on _ACCEPTANCE_BULLET_RE to filter.
            continue
        if not line.lstrip().startswith("-"):
            # Non-bullet, non-blank → block ended.
            break
        m = _ACCEPTANCE_BULLET_RE.match(line)
        if not m:
            continue
        cmd = m.group("cmd").strip()
        if m.group("exits") is not None:
            pred: Predicate = ExitsN(kind="exits", n=int(m.group("exits")))
        elif m.group("eq") is not None:
            pred = StdoutEq(kind="stdout==", value=m.group("eq"))
        elif m.group("ge") is not None:
            pred = StdoutGe(kind="stdout>=", threshold=int(m.group("ge")))
        elif m.group("match") is not None:
            pred = StdoutMatches(kind="stdout-matches", regex=m.group("match"))
        else:
            continue
        claims.append(AcceptanceClaim(
            command=cmd, predicate=pred, raw_line=line.strip()))
    return claims


def _acceptance_optout_reason(phase_body: str) -> Optional[str]:
    """Return the opt-out reason if `**Acceptance:** none — <reason>`,
    otherwise None. Empty reason returns empty string (still opted-out)."""
    m = _ACCEPTANCE_NONE_RE.search(phase_body)
    if not m:
        return None
    return (m.group(1) or "").strip()


def _has_acceptance_header(phase_body: str) -> bool:
    """True if the phase body declares an Acceptance block (with or
    without bullets, with or without the `none` opt-out)."""
    return bool(_ACCEPTANCE_HEADER_RE.search(phase_body)
                or _ACCEPTANCE_NONE_RE.search(phase_body))


@dataclass
class Phase:
    number: int
    title: str
    target_files: List[str] = field(default_factory=list)
    raw_body: str = ""
    status_done: bool = False
    acceptance: List[AcceptanceClaim] = field(default_factory=list)
    optout_reason: Optional[str] = None   # set when `Acceptance: none — …`
    has_acceptance_header: bool = False


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
    """Extract the phase list from a missing-*-feature.md document.

    Under Extreme Rigor, phases are NO LONGER skipped wholesale when
    they carry `**Status:** DONE` — they're tracked with
    `status_done=True` so the supervisor can verify their acceptance
    claims still pass (STATUS_FORGED check). DONE phases without an
    Acceptance block are treated as `LEGACY_ACCEPTED` (informational).

    For purposes of deny-list classification, DONE phases' target
    files are still ignored (they represent completed work whose
    load-bearing references should not re-trigger deny-list halts).
    """
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
        # Anchor to start of line so prose mentions of `**Status:**
        # DONE` inside backticked text or table cells don't falsely
        # flag a phase as DONE. Real Status markers are always
        # line-leading.
        status_done = bool(re.search(
            r"^\*\*Status:\*\*\s+DONE\b", phase_body, re.I | re.M))
        # Target-file scan: skip for DONE phases (their load-bearing
        # references are historical) and skip if a `## What ER would
        # have caught` retrospective sub-section appears (those quote
        # example acceptance blocks, not real targets).
        targets: List[str] = []
        if not status_done:
            seen = set()
            for pm in _PATH_RE.finditer(phase_body):
                p = pm.group(1).strip()
                if p.startswith(("http://", "https://", "git@")):
                    continue
                if p in seen:
                    continue
                seen.add(p)
                targets.append(p)
        acceptance = _parse_acceptance(phase_body)
        optout = _acceptance_optout_reason(phase_body)
        phases.append(Phase(
            number=int(m.group(1)),
            title=m.group(2).strip(),
            target_files=targets,
            raw_body=phase_body.strip(),
            status_done=status_done,
            acceptance=acceptance,
            optout_reason=optout,
            has_acceptance_header=_has_acceptance_header(phase_body),
        ))
    return phases


# ---------------------------------------------------------------------------
# Extreme Rigor: acceptance executor + safety validator
# ---------------------------------------------------------------------------

# Tokens forbidden in acceptance commands. Acceptance must be
# read-only: no state mutation, no network, no multi-statement
# shell. The supervisor halts with `CLAIM_REJECTED` before running
# any rejected claim.
_FORBIDDEN_TOKENS = {
    # Destructive git
    "--hard", "--force",
    "push", "commit", "rebase", "clean",
    # Filesystem mutation
    "rm", "mv", "dd", "chmod", "chown",
    # Network egress
    "curl", "wget",
    # Note: `-f` is intentionally NOT here — `test -f <file>` is the
    # canonical file-exists check and a perfectly valid acceptance
    # idiom. The truly destructive `-f` forms (`push -f`, `clean -f`)
    # are caught by the partner verb token.
}
# Multi-shell-statement separators we forbid.
_FORBIDDEN_SEPARATORS = (";", "&&", "||")
# `gh api` is multi-token; check specially.
_FORBIDDEN_PREFIXES = ("gh api", "gh pr ", "gh issue ")


def _validate_acceptance_safety(claim: AcceptanceClaim) -> Optional[str]:
    """Return rejection reason if `claim` violates the safety
    perimeter, else None. Token-level check — not a security boundary,
    a sanity check against accidental mutation in acceptance claims.

    Forbidden shell metacharacters:
      `;`, `&&`, `||`            — multi-statement (non-atomic claim)
      `>` (output redirect)      — file-system write
      `>>`                       — file-system append
      backtick substitution      — runs arbitrary nested command
      `$(...)`                   — runs arbitrary nested command
      `<(...)`, `>(...)`         — process substitution

    Explicitly ALLOWED (common safe idioms):
      `|`                         — pipe (no state mutation)
      `2>&1`, `1>&2`, etc.        — fd duplication (no file write)
      `< file`                    — input redirect (read-only)
    """
    cmd = claim.command
    # Multi-statement separators
    for sep in _FORBIDDEN_SEPARATORS:
        if sep in cmd:
            return f"forbidden separator {sep!r} (acceptance must be atomic)"
    # Token-level forbidden words
    for tok in _FORBIDDEN_TOKENS:
        if re.search(rf"(?:^|\s){re.escape(tok)}(?:\s|$)", cmd):
            return f"forbidden token {tok!r} (mutation/destruction)"
    # Multi-token forbidden prefixes
    for prefix in _FORBIDDEN_PREFIXES:
        if cmd.startswith(prefix):
            return f"forbidden prefix {prefix!r} (network egress)"
    # Output redirect: `> file` or `>> file`. Allow `2>&1`, `1>&2`,
    # `&>` (caught by `>` followed by digit/&) — the dangerous form
    # is `>` followed by whitespace then a filename, OR `>>` (append).
    if ">>" in cmd:
        return "forbidden `>>` (file append — mutation)"
    # Match `>` NOT preceded by `&` or digit (so `2>&1`, `&>` slip)
    # and NOT followed by `&` or digit (so `>&1`, `>&2` slip).
    if re.search(r"(?<![\d&])>(?![\d&])", cmd):
        return "forbidden `>` output redirect (file write — mutation)"
    # Command substitution
    if "`" in cmd:
        return "forbidden backtick substitution (runs nested command)"
    if "$(" in cmd:
        return "forbidden `$(...)` substitution (runs nested command)"
    # Process substitution
    if "<(" in cmd or ">(" in cmd:
        return "forbidden process substitution `<(...)` / `>(...)`"
    return None


def _check_acceptance(
        claim: AcceptanceClaim,
        cwd: Path,
        timeout: int) -> AcceptanceResult:
    """Execute one acceptance claim and return its result.

    cwd: directory to run in (typically repo root).
    timeout: per-claim subprocess timeout in seconds.
    """
    safety = _validate_acceptance_safety(claim)
    if safety is not None:
        return AcceptanceResult(
            claim=claim, passed=False,
            reason_if_failed=f"CLAIM_REJECTED: {safety}",
        )
    try:
        r = subprocess.run(
            claim.command, shell=True,
            cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return AcceptanceResult(
            claim=claim, passed=False,
            reason_if_failed=f"TIMEOUT (>{timeout}s)",
        )
    except Exception as e:
        return AcceptanceResult(
            claim=claim, passed=False,
            reason_if_failed=f"execution error: {e}",
        )
    stdout = (r.stdout or "").strip()
    p = claim.predicate
    excerpt = stdout[-500:]
    if isinstance(p, ExitsN):
        if r.returncode == p.n:
            return AcceptanceResult(
                claim=claim, passed=True, stdout_excerpt=excerpt)
        return AcceptanceResult(
            claim=claim, passed=False, stdout_excerpt=excerpt,
            reason_if_failed=(
                f"expected exit {p.n}, got {r.returncode}\n"
                f"stderr (last 200 chars): {(r.stderr or '')[-200:]}"
            ),
        )
    if isinstance(p, StdoutEq):
        if stdout == p.value:
            return AcceptanceResult(
                claim=claim, passed=True, stdout_excerpt=excerpt)
        return AcceptanceResult(
            claim=claim, passed=False, stdout_excerpt=excerpt,
            reason_if_failed=f"expected stdout == {p.value!r}, got {stdout!r}",
        )
    if isinstance(p, StdoutGe):
        try:
            actual = int(stdout)
        except ValueError:
            return AcceptanceResult(
                claim=claim, passed=False, stdout_excerpt=excerpt,
                reason_if_failed=f"stdout not an integer: {stdout!r}",
            )
        if actual >= p.threshold:
            return AcceptanceResult(
                claim=claim, passed=True, stdout_excerpt=excerpt)
        return AcceptanceResult(
            claim=claim, passed=False, stdout_excerpt=excerpt,
            reason_if_failed=f"expected stdout >= {p.threshold}, got {actual}",
        )
    if isinstance(p, StdoutMatches):
        if re.search(p.regex, stdout):
            return AcceptanceResult(
                claim=claim, passed=True, stdout_excerpt=excerpt)
        return AcceptanceResult(
            claim=claim, passed=False, stdout_excerpt=excerpt,
            reason_if_failed=f"expected stdout matches /{p.regex}/",
        )
    return AcceptanceResult(
        claim=claim, passed=False, stdout_excerpt=excerpt,
        reason_if_failed=f"unknown predicate kind {p.kind!r}",
    )


# ---------------------------------------------------------------------------
# Verification gate
# ---------------------------------------------------------------------------

@dataclass
class GateStep:
    name: str
    cmd: List[str]
    skip_if_missing: bool = False  # if the tool doesn't exist, skip with PASS
    deep: bool = False             # run only when PYCSL_SUPERVISOR_DEEP=1
    timeout: int = 0               # per-step override; 0 = use default


# Default per-step timeout, overridable via PYCSL_SUPERVISOR_STEP_TIMEOUT
# env var (in seconds). The reference-test corpus can take >10min on a
# cold cache and was the original culprit behind the v1 gate halt — move
# it to "deep" mode by default and require an explicit opt-in.
_DEFAULT_TIMEOUT_SEC = int(os.environ.get("PYCSL_SUPERVISOR_STEP_TIMEOUT", "600"))
_DEEP_MODE = os.environ.get("PYCSL_SUPERVISOR_DEEP", "0") == "1"

GATE_STEPS: List[GateStep] = [
    GateStep("pytest tests/",
             ["pytest", "-q", "tests/"], skip_if_missing=True),
    GateStep("bin/run-reference-tests.sh",
             [str(_PROJECT_ROOT / "bin" / "run-reference-tests.sh")],
             skip_if_missing=True, deep=True, timeout=1800),
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
        if step.deep and not _DEEP_MODE:
            results.append(GateResult(
                step.name + " (deep — set PYCSL_SUPERVISOR_DEEP=1 to enable)",
                True, True, ""))
            continue
        if step.skip_if_missing and not Path(step.cmd[0]).exists():
            results.append(GateResult(step.name, True, True, ""))
            continue
        step_timeout = step.timeout or _DEFAULT_TIMEOUT_SEC
        try:
            r = subprocess.run(
                step.cmd,
                cwd=str(_PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=step_timeout,
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
                                      f"TIMEOUT (>{step_timeout}s)"))
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


def _load_competency_matrix() -> Dict[str, List[str]]:
    """Parse the competency matrix's fenced block → {level_key: [skill names]}.

    Keys are `*` (all levels) or `L1`–`L5`; values are `config/skills/<name>`
    directory names. Returns {} if the file/block is absent.
    """
    matrix: Dict[str, List[str]] = {}
    if not _COMPETENCY_FILE.is_file():
        return matrix
    text = _COMPETENCY_FILE.read_text()
    # The machine block is the fenced ``` … ``` containing `key: a, b` lines.
    # Keys are `*`, `L<n>`, or `L<n>-<Role>` (e.g. `L5-Validator`).
    _key = r"(\*|L\d(?:-[A-Za-z][A-Za-z-]*)?)"
    for block in re.findall(r"```\n(.*?)\n```", text, re.S):
        if not re.search(rf"^\s*{_key}\s*:", block, re.M):
            continue
        for line in block.splitlines():
            m = re.match(rf"^\s*{_key}\s*:\s*(.+?)\s*$", line)
            if m:
                skills = [s.strip() for s in m.group(2).split(",") if s.strip()]
                matrix[m.group(1)] = skills
    return matrix


def _phase_level(phase: "Phase") -> str:
    """The phase's `**Level:** L<n>` tag (line-leading), or '' if none."""
    m = re.search(r"^\*\*Level:\*\*\s*(L\d)\b", phase.raw_body, re.M)
    return m.group(1) if m else ""


def _phase_role(phase: "Phase") -> str:
    """The phase's `**Role:** <Role>` tag (e.g. Validator), or '' if none."""
    m = re.search(r"^\*\*Role:\*\*\s*([A-Za-z][A-Za-z-]*)", phase.raw_body, re.M)
    return m.group(1) if m else ""


def _phase_competency_skills(phase: "Phase",
                             matrix: Dict[str, List[str]]) -> List[str]:
    """Skill names this phase needs: union of the `*` row, the phase's level
    row, and (if a role is tagged) the `L<n>-<Role>` row. Deduped, stable
    order. The role combination is how proof skills (`rocq`/`lean`) reach the
    low-level Validator only."""
    level = _phase_level(phase)
    role = _phase_role(phase)
    keys = ["*"]
    if level:
        keys.append(level)
        if role:
            keys.append(f"{level}-{role}")
    out: List[str] = []
    for key in keys:
        for s in matrix.get(key, []):
            if s not in out:
                out.append(s)
    return out


def _append_resolved_competencies(phases: List["Phase"]) -> None:
    """Append `### 5.1 Resolved per-phase competencies` to the harness-structure
    log (path in $PYCSL_HARNESS_LOG) so a human can review which skills each
    phase's delegate will receive. No-op if the env var / log is absent."""
    log_path = os.environ.get("PYCSL_HARNESS_LOG")
    if not log_path:
        return
    matrix = _load_competency_matrix()
    lines = [
        "", "### 5.1 Resolved per-phase competencies",
        "", "From `config/skills/project-lifecycle/references/competency-matrix.md` "
        "(`**Level:**` tag → skills injected into that phase's delegate prompt):", "",
    ]
    for p in phases:
        lvl = _phase_level(p) or "—"
        role = _phase_role(p)
        tag = f"level {lvl}" + (f", role {role}" if role else "")
        skills = _phase_competency_skills(p, matrix)
        skills_str = ", ".join(f"`{s}`" for s in skills) if skills else "(none)"
        lines.append(f"- **Phase {p.number}** ({tag}): {skills_str}")
    lines.append("")
    try:
        with open(log_path, "a") as f:
            f.write("\n".join(lines))
    except OSError:
        pass


def _build_phase_prompt(phase: "Phase", plan_text: str) -> str:
    """Wrap the coding-LLM scaffold around the phase body + target file contents."""
    if not _CODING_LLM_PROMPT.is_file():
        scaffold = "(coding-llm-prompt.md missing; falling back to bare instructions)"
    else:
        scaffold = _CODING_LLM_PROMPT.read_text()

    # Prepend the supervisor persona so a delegate inherits the ER
    # discipline (gap 11). Best-effort: skip silently if absent.
    persona = ""
    if _AGENT_DESCRIPTION.is_file():
        persona = (
            "## Operate under this persona (agent-feature-supervisor)\n\n"
            + _AGENT_DESCRIPTION.read_text()
            + "\n\n---\n\n"
        )

    # Inject the skills this phase's role needs (competency matrix), as direct
    # text — the role-appropriate knowledge for the delegate.
    skills_block = ""
    level = _phase_level(phase)
    role = _phase_role(phase)
    role_tag = (level or "—") + (f"/{role}" if role else "")
    skill_names = _phase_competency_skills(phase, _load_competency_matrix())
    if skill_names:
        chunks = [f"## Skills for your role ({role_tag})\n"]
        for name in skill_names:
            sk = _SKILLS_ROOT / name / "SKILL.md"
            if sk.is_file():
                chunks.append(f"### Skill: {name}\n\n{sk.read_text()}\n\n---\n")
        skills_block = "\n".join(chunks) + "\n"

    parts = [
        persona,
        scaffold,
        "",
        "---",
        "",
        skills_block,
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
    parts.append("---")
    parts.append("")
    parts.append(FILE_OUTPUT_INSTRUCTION)
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
    # The fenced-block extractor drops the trailing newline before the closing
    # ``` — git then reports "corrupt patch" on the unterminated last line.
    # Normalise to a single terminating newline before applying.
    if diff_text and not diff_text.endswith("\n"):
        diff_text += "\n"
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


# Full-file output contract — far more robust than a unified diff for an
# LLM, which cannot reliably reproduce exact hunk context / line counts. The
# delegate emits the COMPLETE contents of each created/modified file between
# these markers; the supervisor writes the files directly (no patch parsing).
_FILE_BLOCK_RE = re.compile(
    r"^[ \t]*\*\*\* BEGIN FILE:[ \t]*(?P<path>.+?)[ \t]*\*\*\*[ \t]*\n"
    r"(?P<body>.*?)\n[ \t]*\*\*\* END FILE \*\*\*",
    re.S | re.M,
)
_FENCE_RE = re.compile(r"^```[A-Za-z0-9_-]*\n(.*)\n```\s*$", re.S)

FILE_OUTPUT_INSTRUCTION = (
    "## Output format (REQUIRED)\n\n"
    "Output the COMPLETE final contents of every file you create or modify — "
    "NOT a diff. Wrap each file EXACTLY like this, one block per file:\n\n"
    "*** BEGIN FILE: <repo-relative/path.py> ***\n"
    "<the entire file content, verbatim, with no surrounding code fence>\n"
    "*** END FILE ***\n\n"
    "Emit the full content even for a one-line change. Do not abbreviate, do "
    "not use `...`, do not emit a unified diff."
)


def _extract_files(llm_output: str) -> List[Tuple[str, str]]:
    """Extract (path, full-content) pairs from BEGIN/END FILE markers."""
    out: List[Tuple[str, str]] = []
    for m in _FILE_BLOCK_RE.finditer(llm_output):
        body = m.group("body")
        fence = _FENCE_RE.match(body.strip())
        if fence:  # tolerate an accidental code fence around the content
            body = fence.group(1)
        out.append((m.group("path").strip(), body))
    return out


def _write_files(pairs: List[Tuple[str, str]]) -> Tuple[bool, str, List[str]]:
    """Write each (repo-relative path, content). Returns (ok, err, written)."""
    written: List[str] = []
    repo = _PROJECT_ROOT.resolve()
    for rel, content in pairs:
        rel = rel.strip().lstrip("./").lstrip("/")
        target = (_PROJECT_ROOT / rel).resolve()
        try:
            target.relative_to(repo)  # refuse `..`/absolute escapes
        except ValueError:
            return False, f"refusing to write outside repo: {rel!r}", written
        if content and not content.endswith("\n"):
            content += "\n"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        except OSError as e:
            return False, f"write failed for {rel!r}: {e}", written
        written.append(rel)
    return True, "", written


def _rollback_phase(slug: str, phase_number: int,
                    target_files: list[str]) -> bool:
    """Revert per-phase targets to the per-phase start tag. Returns success."""
    tag = _phase_tag(slug, phase_number)
    # Check tag exists
    r = _git("rev-parse", "--verify", tag, check=False)
    if r.returncode != 0:
        return False
    # Restore each target. Files that existed at the tag are restored; files
    # the delegate newly CREATED (absent at the tag — common with full-file
    # output) are deleted, since `git restore` can't revert a non-existent
    # path.
    for target in target_files:
        existed = _git("cat-file", "-e", f"{tag}:{target}",
                       check=False).returncode == 0
        if existed:
            try:
                _git("restore", f"--source={tag}", "--worktree", "--staged",
                     "--", target)
            except RuntimeError:
                return False
        else:
            p = _PROJECT_ROOT / target.lstrip("./").lstrip("/")
            try:
                if p.is_file():
                    p.unlink()
            except OSError:
                return False
            _git("rm", "-f", "--cached", "--ignore-unmatch", "--", target,
                 check=False)
    # Delete the tag (rollback complete)
    _git("tag", "-d", tag, check=False)
    return True


def _delegate_model() -> str:
    """Model used for LLM delegation.

    Resolution order: `PYCSL_LLM_MODEL` env var → `model` key of
    `config/agents-config.json` → a safe Copilot default. A `claude-*`/`gpt-*`
    name routes to the GitHub Copilot CLI; any other name is treated as an
    Ollama tag (HTTP). Previously the delegate read only the env var and
    defaulted to "" — which mis-routed to the (possibly down) Ollama host.
    """
    env = os.environ.get("PYCSL_LLM_MODEL")
    if env:
        return env
    try:
        import json as _json
        cfg = _json.loads(
            (_PROJECT_ROOT / "config" / "agents-config.json").read_text())
        if cfg.get("model"):
            return cfg["model"]
    except Exception:
        pass
    return "claude-sonnet-4.6"


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
            system="You are a coding assistant. Follow the rules in the "
                   "coding-llm-prompt scaffold above. " + FILE_OUTPUT_INSTRUCTION,
            agent_id=AGENT_NAME,
            model=_delegate_model(),
        )
    except Exception as e:
        return False, f"llm_generate raised: {e}"

    # Prefer full-file blocks (robust); fall back to a unified diff.
    files = _extract_files(llm_output)
    if files:
        ok, err, written = _write_files(files)
        if not ok:
            _rollback_phase(slug, phase.number, phase.target_files)
            return False, err
        rollback_targets = sorted(set(phase.target_files) | set(written))
    else:
        diff = _extract_diff(llm_output)
        if not diff:
            return False, "llm output had neither FILE blocks nor a diff block"
        ok, err = _apply_diff(diff)
        if not ok:
            return False, err
        rollback_targets = list(phase.target_files)

    # Re-run the gate (subset — just the cheap steps)
    quick_results = run_gate()
    if not all(r.passed for r in quick_results):
        _rollback_phase(slug, phase.number, rollback_targets)
        return False, "gate-fail (rolled back)"

    # ER gap 6: also evaluate the phase's acceptance claims after the
    # LLM diff applies. Without this, delegation succeeds based on
    # gate alone — exactly the proxy-claim pattern ER exists to
    # prevent. Empty acceptance list means the phase opted out or
    # was caught upstream by the completeness guard.
    if phase.acceptance:
        for claim in phase.acceptance:
            res = _check_acceptance(
                claim, _PROJECT_ROOT, _DEFAULT_TIMEOUT_SEC)
            if not res.passed:
                _rollback_phase(slug, phase.number, rollback_targets)
                return False, (
                    f"acceptance-fail (rolled back): {claim.raw_line!r} → "
                    f"{res.reason_if_failed}"
                )

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
    acceptance_failures: Optional[List[Tuple["Phase", "AcceptanceResult"]]] = None,
    missing_acceptance_phases: Optional[List["Phase"]] = None,
    explanation: Optional[str] = None,
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
    ]
    # Plain-English explanation of what happened, in addition to the
    # machine reason code, so the report is readable without tracing code.
    if explanation:
        lines += ["## What this means", "", explanation, ""]
    lines += [
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

    # ER: missing-acceptance phases
    if missing_acceptance_phases:
        lines += [
            "## Missing Acceptance blocks",
            "",
            "These phases carry neither `**Status:** DONE` nor an "
            "`**Acceptance:**` block. Per Extreme Rigor (see "
            "`feature-supervisor-extreme-rigor.md`), every open phase "
            "must declare machine-checkable acceptance claims so the "
            "supervisor can evaluate \"done\" without asking the human "
            "*what was not done*.",
            "",
        ]
        for p in missing_acceptance_phases:
            lines.append(f"- Phase {p.number} — {p.title}")
        lines.append("")
        lines += [
            "To resolve, add an `**Acceptance:**` block to each phase. "
            "If the phase is intentionally not machine-checkable, use "
            "`**Acceptance:** none — <reason>` to opt out explicitly.",
            "",
        ]

    # ER: acceptance failures (including CLAIM_REJECTED)
    if acceptance_failures:
        lines += ["## Acceptance failures", ""]
        for p, res in acceptance_failures:
            status_tag = "DONE → STATUS_FORGED" if p.status_done else "open"
            lines.append(
                f"### Phase {p.number} — {p.title} ({status_tag})"
            )
            lines.append("")
            lines.append(f"- Claim: `{res.claim.raw_line}`")
            lines.append(f"  - Command: `{res.claim.command}`")
            lines.append(f"  - Predicate: {res.claim.predicate.describe()}")
            lines.append(f"  - Outcome: {res.reason_if_failed}")
            if res.stdout_excerpt:
                lines.append("  - Stdout (last 500 chars):")
                lines.append("    ```")
                for ln in res.stdout_excerpt.splitlines():
                    lines.append(f"    {ln}")
                lines.append("    ```")
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


def _print_halt(out: Path, exit_reason: str, exit_code: int,
                explanation: str,
                review: Optional[List[Tuple[str, Path]]] = None) -> None:
    """Print an explicit, human-readable halt summary to the terminal.

    Beyond the machine reason code, this emits (1) a short plain-English
    paragraph saying what happened and what to do, and (2) the ABSOLUTE
    path of the halt-report (plus any other files worth opening), so the
    operator knows exactly where to look without rebuilding relative
    paths. Mirrors the report's `## What this means` section.
    """
    code = exit_reason.split(":", 1)[0].strip()
    print(f"[{AGENT_NAME}] HALT — {code} (exit {exit_code})")
    for ln in explanation.splitlines():
        if ln.strip():
            print(f"[{AGENT_NAME}]   {ln.rstrip()}")
    print(f"[{AGENT_NAME}]   review:")
    print(f"[{AGENT_NAME}]     halt-report : {out.resolve()}")
    for label, path in (review or []):
        print(f"[{AGENT_NAME}]     {label:<11}: {Path(path).resolve()}")


# ---------------------------------------------------------------------------
# Main loop (v1 — gate-only)
# ---------------------------------------------------------------------------

def supervise(feature_file: Path, skip_gate: bool,
              allow_llm_delegation: bool = False,
              allow_load_bearing: bool = False) -> int:
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
        tags = []
        if p.status_done:
            tags.append("DONE")
        if p.optout_reason is not None:
            tags.append("OPTOUT")
        if p.acceptance:
            tags.append(f"{len(p.acceptance)} claim(s)")
        tag_str = f" [{', '.join(tags)}]" if tags else ""
        print(f"  Phase {p.number}: {p.title} — "
              f"{len(p.target_files)} target file(s){tag_str}")
    print(f"[{AGENT_NAME}] deny-list entries: {len(deny_list)}; "
          f"load-bearing hits: {len(deny_hits)}")

    # Record the competency-matrix resolution into the harness log (§5.1) so a
    # human can review which skills each phase's delegate receives.
    _append_resolved_competencies(phases)

    # ---- ER: plan-completeness guard (MISSING_ACCEPTANCE) ----
    # An open phase (not DONE) lacking an Acceptance block AND lacking
    # an explicit `none — <reason>` opt-out is incomplete. Halt
    # before running gate/acceptance — the plan itself is malformed.
    missing_acceptance = [
        p for p in phases
        if not p.status_done
        and not p.has_acceptance_header
    ]
    if missing_acceptance:
        reason = (
            f"{REASON_MISSING_ACCEPTANCE}: {len(missing_acceptance)} phase(s) "
            f"lack an **Acceptance:** block. Under Extreme Rigor every open "
            f"phase must declare its acceptance claims, or opt out via "
            f"`**Acceptance:** none — <reason>`."
        )
        miss_nums = ', '.join(str(p.number) for p in missing_acceptance)
        explanation = (
            f"{len(missing_acceptance)} open phase(s) (phase(s) {miss_nums}) "
            f"declare neither `**Status:** DONE` nor an `**Acceptance:**` block, "
            f"so they have no machine-checkable definition of done — the plan "
            f"is malformed and nothing was run yet. Add an `**Acceptance:**` "
            f"block to each (a command + predicate per `acceptance-syntax.md`), "
            f"or opt out explicitly with `**Acceptance:** none — <reason>` for "
            f"research/scoping phases.\n"
            f"See the report's `## Missing Acceptance blocks` section."
        )
        out = write_halt_report(
            feature_file, phases, deny_hits, [], reason,
            missing_acceptance_phases=missing_acceptance,
            explanation=explanation,
        )
        _print_halt(out, reason, EXIT_HUMAN_NEEDED, explanation,
                    review=[("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=75 feature={feature_file.name} "
            f"reason={REASON_MISSING_ACCEPTANCE} "
            f"missing={len(missing_acceptance)}")
        return EXIT_HUMAN_NEEDED

    # ---- ER: acceptance evaluation ----
    # Run acceptance claims for every phase that has them. DONE phases
    # with claims must still pass (STATUS_FORGED if not). DONE phases
    # without claims are LEGACY_ACCEPTED (informational, no halt).
    # Opt-out phases are skipped entirely.
    acceptance_failures: List[Tuple[Phase, AcceptanceResult]] = []
    any_rejection = False
    legacy_count = 0
    optout_count = 0
    claims_evaluated = 0
    if phases:
        print(f"[{AGENT_NAME}] evaluating acceptance claims ...")
    for p in phases:
        if p.optout_reason is not None:
            optout_count += 1
            print(f"  [OPTOUT] Phase {p.number} — "
                  f"reason: {p.optout_reason or '(unspecified)'}")
            continue
        if p.status_done and not p.acceptance:
            legacy_count += 1
            print(f"  [LEGACY_ACCEPTED] Phase {p.number} — "
                  f"DONE without Acceptance block (grandfathered)")
            continue
        if not p.acceptance:
            # Shouldn't reach here: completeness guard caught it.
            continue
        all_pass = True
        for claim in p.acceptance:
            claims_evaluated += 1
            res = _check_acceptance(
                claim, _PROJECT_ROOT, _DEFAULT_TIMEOUT_SEC)
            if not res.passed:
                all_pass = False
                acceptance_failures.append((p, res))
                if res.reason_if_failed.startswith("CLAIM_REJECTED"):
                    any_rejection = True
        tag = "STATUS_VERIFIED" if (p.status_done and all_pass) else (
              "PASS" if all_pass else "FAIL")
        print(f"  [{tag}] Phase {p.number} — {len(p.acceptance)} claim(s)")

    # In delegation mode the failing claims are exactly the work to be done,
    # so don't halt here — fall through to delegation (its per-phase gate +
    # rollback is the arbiter). CLAIM_REJECTED (an unsafe acceptance command)
    # still halts: that is a malformed plan, not work to delegate.
    _will_delegate = allow_llm_delegation and (not deny_hits or allow_load_bearing)
    if acceptance_failures and (not _will_delegate or any_rejection):
        if any_rejection:
            reason_code = REASON_CLAIM_REJECTED
        elif any(p.status_done for (p, _) in acceptance_failures):
            reason_code = REASON_STATUS_FORGED
        else:
            reason_code = REASON_ACCEPTANCE_FAILED
        n_fail = len(acceptance_failures)
        n_pass = claims_evaluated - n_fail
        reason = (
            f"{reason_code}: {n_fail} acceptance "
            f"claim(s) failed. See the Acceptance failures section "
            f"of the halt-report for details."
        )
        if reason_code == REASON_STATUS_FORGED:
            explanation = (
                f"{n_fail} of {claims_evaluated} acceptance claim(s) failed, and "
                f"at least one belongs to a phase marked `**Status:** DONE` — so "
                f"that DONE marker is now untrue (STATUS_FORGED). An acceptance "
                f"claim is a phase's definition of done; it re-runs every "
                f"invocation. A DONE phase whose claim fails means the work it "
                f"claimed has regressed or never shipped.\n"
                f"Open the report's `## Acceptance failures` section: each entry "
                f"shows the exact command, predicate, and actual outcome."
            )
        elif reason_code == REASON_CLAIM_REJECTED:
            explanation = (
                f"An acceptance command was refused by the read-only safety "
                f"classifier (it tried to mutate state or reach the network). "
                f"Acceptance claims must be read-only. Rewrite the command "
                f"read-only, or move the mutation into a `bin/*` script and have "
                f"the claim invoke that script.\n"
                f"The offending command is in the report's `## Acceptance "
                f"failures` section ({n_fail} of {claims_evaluated} claim(s) failed)."
            )
        else:
            explanation = (
                f"{n_pass} of {claims_evaluated} acceptance claim(s) passed; "
                f"{n_fail} failed. A claim is the phase's definition of done; it "
                f"fails when the file, flag, or output it checks does not exist "
                f"yet. The gate passes what is already present and fails what is "
                f"not yet built — so this halt means the feature has not shipped "
                f"those phases yet, NOT that anything is broken (a claim "
                f"referencing an existing, already-verified artifact still "
                f"passes).\n"
                f"Open the report's `## Acceptance failures` section: each entry "
                f"shows the command, the predicate, and the actual outcome (e.g. "
                f"\"File '…' not found\" or \"unrecognized arguments\")."
            )
        out = write_halt_report(
            feature_file, phases, deny_hits, [], reason,
            acceptance_failures=acceptance_failures,
            explanation=explanation,
        )
        _print_halt(out, reason, EXIT_HUMAN_NEEDED, explanation,
                    review=[("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=75 feature={feature_file.name} "
            f"reason={reason_code} "
            f"failures={n_fail}")
        return EXIT_HUMAN_NEEDED

    if legacy_count:
        print(f"[{AGENT_NAME}] {legacy_count} legacy DONE phase(s) "
              f"grandfathered (no Acceptance to verify).")
    if optout_count:
        print(f"[{AGENT_NAME}] {optout_count} phase(s) opted out of acceptance.")

    gate_results: List[GateResult] = []

    # 1.4a — LLM delegation (off by default). Only invoked when the
    # flag is set AND there are no deny-list hits AND there are
    # phases that have target files.
    delegation_results: list[tuple[int, bool, str]] = []
    if allow_llm_delegation and (not deny_hits or allow_load_bearing):
        slug = _slug(feature_file.stem)
        delegate_phases = [p for p in phases if p.target_files and not p.status_done]
        if deny_hits and allow_load_bearing:
            print(f"[{AGENT_NAME}] *** --allow-load-bearing: delegating "
                  f"LOAD-BEARING phases to the coding LLM. Each edit must pass "
                  f"the full gate or it is ROLLED BACK; surviving diffs STILL "
                  f"REQUIRE human review before merge. ***")
        if not delegate_phases:
            print(f"[{AGENT_NAME}] --allow-llm-delegation: no open phases "
                  f"with target files to delegate.")
        else:
            print(f"[{AGENT_NAME}] --allow-llm-delegation: delegating "
                  f"{len(delegate_phases)} phase(s) (LLM-driven; per-phase "
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
    if deny_hits and not (allow_llm_delegation and allow_load_bearing):
        n = len(deny_hits)
        hit_phases = sorted({ph for ph, _, _ in deny_hits})
        reason = (
            f"Human-needed: {n} load-bearing file(s) named in "
            f"feature-plan phases. Supervisor (v1, gate-only) does not "
            f"edit load-bearing files autonomously."
        )
        explanation = (
            f"{n} phase target(s) (phase(s) {', '.join(map(str, hit_phases))}) "
            f"match the load-bearing deny-list. These files are the "
            f"parser/IR/emitter pipeline and normative docs: a wrong edit "
            f"silently breaks the proof pipeline, so the supervisor is "
            f"gate-only (v1) and never edits them autonomously — even when "
            f"every acceptance claim passes. A human (or an explicitly "
            f"delegated, reviewed coding session) must make and review those "
            f"edits, then re-run the supervisor to confirm the gate is green.\n"
            f"See the report's `## Load-bearing deny-list hits` section for the "
            f"exact phase→file→deny-list-entry matches."
        )
        out = write_halt_report(feature_file, phases, deny_hits, gate_results,
                                reason, explanation=explanation)
        _print_halt(out, reason, EXIT_HUMAN_NEEDED, explanation,
                    review=[("deny-list", _LOAD_BEARING_FILE),
                            ("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=75 feature={feature_file.name} "
            f"deny_hits={n}")
        return EXIT_HUMAN_NEEDED

    if gate_results and not all(r.passed for r in gate_results):
        failed_steps = ', '.join(r.step for r in gate_results
                                 if not r.passed and not r.skipped)
        reason = "Gate failure: one or more verification steps failed."
        explanation = (
            f"The verification gate ran but a step failed: {failed_steps}. "
            f"This is an infrastructure/regression failure (the test suite, "
            f"audit, or doc-coherency itself is red), independent of the "
            f"feature's acceptance claims. Fix the failing step, then re-run.\n"
            f"See the report's `## Verification gate` section for the last "
            f"lines of the failing step's output."
        )
        out = write_halt_report(feature_file, phases, deny_hits, gate_results,
                                reason, explanation=explanation)
        _print_halt(out, reason, EXIT_GATE_FAIL, explanation,
                    review=[("feature file", feature_file)])
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
        explanation = (
            f"Under `--allow-llm-delegation`, the coding-LLM delegate for "
            f"phase {failed[0][0]} did not land a gate-green diff "
            f"({failed[0][1]}). The working tree was restored from the "
            f"per-phase git tag, so no partial edit remains. Inspect the "
            f"phase, refine the plan or implement it manually, then re-run."
        )
        out = write_halt_report(feature_file, phases, deny_hits, [], reason,
                                explanation=explanation)
        _print_halt(out, reason, EXIT_GATE_FAIL, explanation,
                    review=[("feature file", feature_file)])
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
    parser.add_argument("--allow-load-bearing", action="store_true",
                        help="DANGER: with --allow-llm-delegation, also "
                        "delegate phases that touch load-bearing files (the "
                        "parser/IR/emitter). Each delegated edit must still "
                        "pass the full gate or it is rolled back, and the "
                        "surviving diff REQUIRES human review before merge. "
                        "Relaxes the soundness perimeter — use deliberately.")
    args = parser.parse_args()
    if args.allow_load_bearing and not args.allow_llm_delegation:
        print(f"[{AGENT_NAME}] --allow-load-bearing implies --allow-llm-delegation "
              f"— enabling LLM delegation.")
        args.allow_llm_delegation = True
    return supervise(args.feature_file, args.skip_gate,
                     allow_llm_delegation=args.allow_llm_delegation,
                     allow_load_bearing=args.allow_load_bearing)


if __name__ == "__main__":
    sys.exit(main())
