"""Subprocess wrapper around the pycsl CLI.

`run_pycsl(path)` shells out to `src/pycsl/pycsl.py`, captures stdout
and stderr, and parses the goal-by-goal output into a `Verdict`. The
parser is deliberately tolerant — anything it doesn't recognize ends up
in `Verdict.stdout`/`stderr` and the obligation count comes out as zero,
which the caller sees as a non-success.

The pycsl entry point is invoked through the same Python interpreter
that's running the tool, so virtualenv selection just works.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .verdict import ObligationResult, ObligationStatus, Verdict


# Resolve the pycsl entry point relative to this file. We can't rely on
# `pycsl` being on PATH, and we want to invoke through the same
# interpreter so virtualenv selection is automatic.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_PYCSL_SCRIPT = _REPO_ROOT / "src" / "pycsl" / "pycsl.py"


# Lines look like:
#   Sub-goal Postcondition of goal test_precondition'vc.
#   Sub-goal of goal foo'vc.
_SUBGOAL_RE = re.compile(
    r"^Sub-goal\s+(?P<kind>.*?)\s*of\s+goal\s+(?P<thm>\S+?)\.\s*$"
)

# Lines look like:
#   Prover result is: Valid (0.01s, 154 steps).
#   Prover result is: Unknown (sat) (0.01s, 266 steps).
#   Prover result is: Timeout.
_RESULT_RE = re.compile(r"^Prover result is:\s*(?P<status>.+?)\.\s*$")


def run_pycsl(
    annotated_path: str | os.PathLike,
    *,
    extra_args: Sequence[str] = (),
    timeout: float | None = 120.0,
    no_proof: bool = False,
) -> Verdict:
    """Invoke pycsl on `annotated_path` and parse the result.

    Parameters:
      annotated_path : the annotated .py file to verify
      extra_args     : passed through verbatim to the pycsl CLI
                       (e.g. ["--memory-model", "hoare", "-p", "Alt-Ergo,2.6.2,"])
      timeout        : wall-clock limit for the whole pycsl invocation;
                       None disables it
      no_proof       : pass `--no-proof` to short-circuit Why3, useful for
                       transpile-only smoke tests

    Returns a Verdict — never raises on prover failure (that's a normal
    "exit 1, obligations have non-Valid status" outcome). Raises only
    on subprocess errors (file not found, timeout, etc.).
    """
    if not _PYCSL_SCRIPT.exists():
        raise FileNotFoundError(f"pycsl entry point not found at {_PYCSL_SCRIPT}")

    cmd = [sys.executable, str(_PYCSL_SCRIPT)]
    if no_proof:
        cmd.append("--no-proof")
    cmd.extend(extra_args)
    cmd.append(str(annotated_path))

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    obligations = _parse_obligations(proc.stdout)
    return Verdict(
        exit_code=proc.returncode,
        obligations=obligations,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _parse_obligations(stdout: str) -> list[ObligationResult]:
    """Walk stdout pairing Sub-goal headers with Prover result lines."""
    results: list[ObligationResult] = []
    pending_thm: str | None = None
    pending_kind: str = ""

    for raw in stdout.splitlines():
        line = raw.strip()
        m = _SUBGOAL_RE.match(line)
        if m:
            pending_thm = m.group("thm")
            pending_kind = m.group("kind").strip()
            continue
        m = _RESULT_RE.match(line)
        if m and pending_thm is not None:
            detail = m.group("status").strip()
            results.append(
                ObligationResult(
                    theorem=pending_thm,
                    kind=pending_kind,
                    status=_classify(detail),
                    detail=detail,
                )
            )
            pending_thm, pending_kind = None, ""

    return results


def _classify(detail: str) -> ObligationStatus:
    """Map a Why3 prover-result string onto an ObligationStatus."""
    head = detail.split()[0] if detail else ""
    mapping = {
        "Valid": ObligationStatus.VALID,
        "Unknown": ObligationStatus.UNKNOWN,
        "Timeout": ObligationStatus.TIMEOUT,
        "Invalid": ObligationStatus.INVALID,
        "Failure": ObligationStatus.FAILURE,
        "HighFailure": ObligationStatus.HIGH_FAILURE,
    }
    return mapping.get(head, ObligationStatus.UNKNOWN)
