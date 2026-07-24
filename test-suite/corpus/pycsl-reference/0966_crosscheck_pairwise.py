"""class-variant-impl.md §F5: a POSITIVE witness for the crosscheck_ir.py
`IRCrossCheckResult.pairwise` carrier.

`pairwise` returns `Dict[str, Optional[bool]]` — inlined option-lifted structural
comparisons of the `option term` canon fields:

    {"a==b": None if self.A is None or self.B is None else self.A == self.B, ...}

which lowers to `map string (option (option bool))` (a total `ghost let`) where
each key maps to `Some <cmp>` and `<cmp>` is the DEFINED structural `term_eq`
(§F4) wrapped `None` when either canon is absent. The dict-presence wrapper
(`Some _`) is DISJOINT from the value's own Python `Optional[bool]` (`option
bool`): all three keys are PRESENT, the VALUE is `None` when a side is missing.

PROVES. The recognizer is fail-closed and mutation-flowing: the `==` operands
must be EXACTLY the two fields tested for `None` (see the twin 0967, where a
different field mapping changes this file's emission). A facade (a canned map
that ignores the fields, an int-hash equality, or a 2-ctor collapse) would change
the emission or break the proof. Gated on `_has_opaque_term_fields` +
`_term_adt_spec` -> fires on 0 other programs (corpus + every mirror
byte-identical).
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
            "rocq==lean":     None if self.rocq_canon is None or self.lean_canon is None else self.rocq_canon == self.lean_canon,
            "rocq==registry": None if self.rocq_canon is None or self.registry_canon is None else self.rocq_canon == self.registry_canon,
            "lean==registry": None if self.lean_canon is None or self.registry_canon is None else self.lean_canon == self.registry_canon,
        }
