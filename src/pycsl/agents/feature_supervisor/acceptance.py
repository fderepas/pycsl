from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ._common import *

__all__ = [
    'Predicate',
    'ExitsN',
    'StdoutEq',
    'StdoutGe',
    'StdoutMatches',
    'AcceptanceClaim',
    'AcceptanceResult',
    '_ACCEPTANCE_BULLET_RE',
    '_ACCEPTANCE_NONE_RE',
    '_ACCEPTANCE_HEADER_RE',
    '_parse_acceptance',
    '_acceptance_optout_reason',
    '_has_acceptance_header',
    '_FORBIDDEN_TOKENS',
    '_FORBIDDEN_SEPARATORS',
    '_FORBIDDEN_PREFIXES',
    '_validate_acceptance_safety',
    '_check_acceptance',
]

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

