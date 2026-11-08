"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, T-set/list
leaf): a POSITIVE witness for the `flatten_arrow_chain` while-spine TUPLE walker
over the class-instance VARIANT ADT.

`split_chain(t: Expr) -> Tuple[List[Expr], Expr]` walks down a right-leaning
`Bin("->", …)` chain, collecting each `cur.lhs` into a list and advancing to
`cur.rhs`, returning `(hyps, cur)`. It lowers onto a structural recursion
`split_chain__go (v_cur: term) (acc: list term) : (list term, term) variant
{ v_cur }` over the certified `term` inductive — the Why3-native tuple return, an
inline DEFINED `__app` list append, and a VC-free `val __streq` string guard.
Structurally terminating, NO axiom (ledger 3).

`norm` seeds the ctor set. PROVES. A facade regression (mis-reading the append
field `cur.lhs`, the advance field `cur.rhs`, or the `"->"` guard string)
changes this file's emission — the mutation-test / vacuity-gate non-vacuity lock
(the 0955 twin discriminates the append field). Gated on `needs_term` => every
other corpus file byte-identical.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


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
def split_chain(t: Expr) -> Tuple[List[Expr], Expr]:
    hyps: List[Expr] = []
    cur = t
    while isinstance(cur, Bin) and cur.op == "->":
        hyps.append(cur.lhs)
        cur = cur.rhs
    return hyps, cur
