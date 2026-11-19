"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_crosscheck_term_method` bespoke lowering
dropped the declared contract.

Derived from corpus 0964 (same body; contract changed): `IRCrossCheckResult.any_unsupported` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0964 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


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

    #@ ensures False
    #@ assigns \nothing
    def any_unsupported(self) -> bool:
        return any(isinstance(c, Unsupported)
                   for c in (self.rocq_canon, self.lean_canon,
                             self.registry_canon)
                   if c is not None)

    #@ assigns \nothing
    def all_present_unsupported(self) -> bool:
        canons = [c for c in (self.rocq_canon, self.lean_canon,
                              self.registry_canon) if c is not None]
        if not canons:
            return False
        return all(isinstance(c, Unsupported) for c in canons)

    #@ assigns \nothing
    def provers_agree(self) -> bool:
        if self.rocq_canon is None or self.lean_canon is None:
            return True
        return self.rocq_canon == self.lean_canon

    #@ assigns \nothing
    def all_agree(self) -> bool:
        canons = [c for c in
                  (self.rocq_canon, self.lean_canon, self.registry_canon)
                  if c is not None]
        if not canons:
            return False
        return all(c == canons[0] for c in canons)
