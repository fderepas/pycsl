from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ._common import *

__all__ = [
    'GateStep',
    'GATE_STEPS',
    'GateResult',
    'run_gate',
]

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
    # `\trusted`-in-stubs census (informational; exits 0). Per-phase strict
    # enforcement (`--strict <target stub>`) is applied where a phase migrates a
    # stub — see config/skills/agent-stdlib-annotate/SKILL.md.
    GateStep("bin/check-no-trusted-stubs.py",
             [str(_PROJECT_ROOT / "bin" / "check-no-trusted-stubs.py")],
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

