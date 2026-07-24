"""class-variant-impl.md §F5: the DISCRIMINATING TWIN of 0966.

Identical scaffold, but the single `pairwise` entry compares a DIFFERENT field
pair — `rocq_canon` vs `registry_canon` (0966's first entry is `rocq_canon` vs
`lean_canon`). The recognizer READS the actual `None`-tested + `==` operand
fields, so this file's emitted `.mlw` differs from 0966's (`self.registry_canon`
in the first `term_eq` match instead of `self.lean_canon`). Both PROVE — the
carrier forces `ensures True` (no postcondition evil-twin), so the twin is a
BYTE-difference witness, not a proof-failure witness: it demonstrates the
lowering is not a canned emission (mutation-test lock).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Unsupported:
    reason: str
    raw: str


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "Term"
    rhs: "Term"


Term = "Unsupported | Var | Bin"


#@ requires True
#@ ensures True
#@ assigns \nothing
def has_unsup(t: Term) -> bool:
    if isinstance(t, Unsupported):
        return True
    if isinstance(t, Var):
        return False
    if isinstance(t, Bin):
        return has_unsup(t.lhs) or has_unsup(t.rhs)
    raise TypeError("unknown")


@dataclass
class IRCrossCheckResult:
    registry_raw: str = ""
    rocq_canon: Optional[Term] = None
    lean_canon: Optional[Term] = None
    registry_canon: Optional[Term] = None

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def pairwise(self) -> Dict[str, Optional[bool]]:
        return {
            "rocq==lean":     None if self.rocq_canon is None or self.registry_canon is None else self.rocq_canon == self.registry_canon,
            "rocq==registry": None if self.rocq_canon is None or self.registry_canon is None else self.rocq_canon == self.registry_canon,
            "lean==registry": None if self.lean_canon is None or self.registry_canon is None else self.lean_canon == self.registry_canon,
        }
