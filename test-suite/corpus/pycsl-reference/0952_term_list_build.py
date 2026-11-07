"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, T-set/list
leaf): a POSITIVE witness for the `mk_arrow_chain` list-fold BUILDER over the
class-instance VARIANT ADT.

`build_chain(hyps: List[Expr], conclusion: Expr) -> Expr` seeds an accumulator
with `conclusion` and, over `reversed(hyps)`, wraps it in a `Bin("->", h, out)`
constructor — a right-leaning chain builder. It lowers onto a structural fold
`build_chain__go (l: list term) (acc: term) : term` over the certified `term`
inductive (reversed => a foldr: the ctor wraps `__go rest acc`). Structurally
terminating (`variant { l }`), NO axiom (all constructors are the `term`
variant; ledger 3).

`norm` seeds the ctor set (the spec is built from isinstance-dispatch); it is a
plain identity/rebuild transform.

PROVES. A facade regression (dropping the recursion, mis-copying the `"->"`
ctor string, or losing the reversed foldr direction) changes this file's
emission — the mutation-test / vacuity-gate non-vacuity lock (the carrier forces
`ensures True`, so no postcondition evil-twin; the 0953 twin discriminates the
ctor string). Gated on `needs_term` => every other corpus file byte-identical.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Leaf:
    name: str


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "Expr"
    rhs: "Expr"


Expr = "Leaf | Bin"


#@ requires True
#@ ensures True
#@ assigns \nothing
def norm(e: Expr) -> Expr:
    if isinstance(e, Leaf):
        return e
    if isinstance(e, Bin):
        return Bin(e.op, norm(e.lhs), norm(e.rhs))
    raise TypeError("unknown")


#@ requires True
#@ ensures True
#@ assigns \nothing
def build_chain(hyps: List[Expr], conclusion: Expr) -> Expr:
    out: Expr = conclusion
    for h in reversed(hyps):
        out = Bin("->", h, out)
    return out
