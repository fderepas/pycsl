"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, §F3+§F4): the
DISCRIMINATING TWIN of 0964: `any_unsupported` tests `isinstance(c, Var)`
(not `Unsupported`), so the emitted match arm is `Some (Var _)` (arity 1) rather
than `Some (Unsupported _ _)` (arity 2) — a BYTE-DIFFERENT emission that still
PROVES. The isinstance target ctor + its arity genuinely flow (non-facade).

Once the certified 9-ctor `term` inductive is available in the file (here the
`Term = Unsupported | Var | Bin` union + the `has_unsup` isinstance-dispatch
fold that seeds it), the `IRCrossCheckResult` `Optional[Term]` canon fields are
the FAITHFUL `option term` (§F3, was the presence-only `option int`), so:

  * `any_unsupported` / `all_present_unsupported` — `isinstance(c, Unsupported)`
    over the canon fields lowers to a `Some (Unsupported _ _)` match arm over the
    REAL inductive (no int-hash, no 1/2-ctor collapse);
  * `provers_agree` / `all_agree` — `c == d` on Term lowers to the DEFINED
    structural `term_eq` (§F4): total, mutually recursive with `term_list_eq` /
    `strlist_eq`, structural `variant` (Why3-intrinsic termination over the same
    Phase2i-certified inductive — NO new certificate, NO axiom; `pystr_eq` is a
    VC-free `val`).

PROVES. A facade (a 2-ctor `Unsupported|Other` collapse, an int-hash isinstance,
or a canned emission that ignores the field / quantifier / isinstance target)
would change this file's emission or break its proof — the mutation-test /
vacuity non-vacuity lock (the carrier forces `ensures True`, so there is no
postcondition evil-twin). Gated on the (class, field) allow-list +
`_has_opaque_term_fields` -> fires on 0 other programs (corpus + every other
mirror byte-identical).
"""
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
    def any_unsupported(self) -> bool:
        return any(isinstance(c, Var)
                   for c in (self.rocq_canon, self.lean_canon,
                             self.registry_canon)
                   if c is not None)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def all_present_unsupported(self) -> bool:
        canons = [c for c in (self.rocq_canon, self.lean_canon,
                              self.registry_canon) if c is not None]
        if not canons:
            return False
        return all(isinstance(c, Unsupported) for c in canons)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def provers_agree(self) -> bool:
        if self.rocq_canon is None or self.lean_canon is None:
            return True
        return self.rocq_canon == self.lean_canon

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def all_agree(self) -> bool:
        canons = [c for c in
                  (self.rocq_canon, self.lean_canon, self.registry_canon)
                  if c is not None]
        if not canons:
            return False
        return all(c == canons[0] for c in canons)
