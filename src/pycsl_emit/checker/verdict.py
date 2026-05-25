"""Structured verdict produced by the pycsl checker.

Mirrors the goal-by-goal output of `src/pycsl/pycsl.py`. A verdict tells
the caller, for every Why3 proof obligation generated from the annotated
Python, what the prover concluded.

Status values mirror the strings Why3 emits:

  Valid             - obligation discharged
  Unknown           - prover ran but couldn't decide (includes "Unknown (sat)")
  Timeout           - prover hit its timeout
  Invalid           - prover proved the negation
  Failure           - prover crashed or hit a tool error
  HighFailure       - resource limit (memory/CPU) hit

Anything Why3 prints we don't recognize is normalized to `Unknown`.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional


class ObligationStatus(str, enum.Enum):
    VALID = "Valid"
    UNKNOWN = "Unknown"
    TIMEOUT = "Timeout"
    INVALID = "Invalid"
    FAILURE = "Failure"
    HIGH_FAILURE = "HighFailure"


@dataclass(frozen=True)
class ObligationResult:
    """One Why3 sub-goal."""
    theorem: str          # e.g. "test_precondition'vc"
    kind: str             # e.g. "Postcondition", "LoopInvariant init", ""
    status: ObligationStatus
    detail: str = ""      # raw status line, useful for error reports


@dataclass
class Verdict:
    """End-to-end pycsl run summary."""
    exit_code: int
    obligations: list[ObligationResult] = field(default_factory=list)
    # Captured for diagnostics; not parsed beyond surface inspection.
    stdout: str = ""
    stderr: str = ""

    @property
    def valid_count(self) -> int:
        return sum(1 for o in self.obligations if o.status is ObligationStatus.VALID)

    @property
    def total(self) -> int:
        return len(self.obligations)

    @property
    def all_valid(self) -> bool:
        return self.exit_code == 0 and self.total > 0 and self.valid_count == self.total

    def unproven(self) -> list[ObligationResult]:
        return [o for o in self.obligations if o.status is not ObligationStatus.VALID]

    def summary(self) -> str:
        if self.exit_code != 0 and self.total == 0:
            return f"pycsl run failed (exit {self.exit_code}); no obligations parsed"
        return f"{self.valid_count}/{self.total} obligations Valid (exit {self.exit_code})"
