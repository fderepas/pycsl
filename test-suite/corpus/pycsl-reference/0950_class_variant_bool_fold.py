"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3): a POSITIVE
witness for the class-instance VARIANT ADT carrier.

A `\trusted`-free bool existence fold that isinstance-dispatches over a frozen-
dataclass UNION (`Expr = Leaf | Bad | Neg | Pair`) and reads named fields
(`e.arg`/`e.left`/`e.right`) is lowered onto a Why3 VARIANT `term = Leaf string
| Bad string | Neg string term | Pair string term term` and the isinstance-
if-chain becomes a TOTAL positional `match`. Structurally terminating; co-landed
axiom-free with the Rocq `Phase2i_TermIR.v` / Lean `TermIR.lean` certificate
(ledger 3). PROVES — a facade regression (a template that dropped the field read
or the arm-per-constructor structure) would change this file's emission or break
its proof (the mutation-test / vacuity-gate non-vacuity lock; the carrier forces
`ensures True`, so there is no postcondition evil-twin, exactly as the pyval
walkers). The recognizer is fail-closed + gated on `needs_term`, so every other
corpus file emits byte-identically.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Leaf:
    name: str


@dataclass(frozen=True)
class Bad:
    reason: str


@dataclass(frozen=True)
class Neg:
    op: str
    arg: "Expr"


@dataclass(frozen=True)
class Pair:
    op: str
    left: "Expr"
    right: "Expr"


Expr = "Leaf | Bad | Neg | Pair"


#@ requires True
#@ ensures True
#@ assigns \nothing
def has_bad(e: Expr) -> bool:
    if isinstance(e, Bad):
        return True
    if isinstance(e, Leaf):
        return False
    if isinstance(e, Neg):
        return has_bad(e.arg)
    if isinstance(e, Pair):
        return has_bad(e.left) or has_bad(e.right)
    raise TypeError("unknown")
