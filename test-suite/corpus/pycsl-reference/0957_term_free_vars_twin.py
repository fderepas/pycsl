"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, T-set/list
leaf): a DISCRIMINATING TWIN for the `free_vars` set-of-strings catamorphism over
the class-instance VARIANT ADT.

`fvs(e: Expr) -> set` computes the free-variable name set: a singleton `{e.name}`
at a leaf, a list-union fold over `e.args`, a `|`-union over the two children of
`Bin`, and a `-`-difference `fvs(body) - set(binders)` at a binder node. It
lowers onto a set-of-strings catamorphism where a returned `set` is
`map string bool` (the certified L1 set repr): union / diff are pointwise
`orb` / `andb (… ) (notb …)`, the singleton uses the bare abstract `val
__set_add` (result no VC constrains — the walk contract is `ensures True`; the
`pystr_eq` precedent, NOT an axiom). Structural mutual `variant { v_e }` /
`variant { l }` over the certified `term` inductive; NO axiom (ledger 3).

PROVES. A facade regression (swapping the `-` diff for `|`, dropping the
list-union fold, or mis-reading the binder field) changes this file's emission —
the mutation-test / vacuity-gate non-vacuity lock (the 0957 twin discriminates
the diff vs union). Gated on `needs_term` => every other corpus file
byte-identical.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Leaf:
    name: str


@dataclass(frozen=True)
class App:
    head: str
    args: Tuple["Expr", ...]


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "Expr"
    rhs: "Expr"


@dataclass(frozen=True)
class Quant:
    binders: Tuple[str, ...]
    body: "Expr"


Expr = "Leaf | App | Bin | Quant"


#@ requires True
#@ ensures True
#@ assigns \nothing
def fvs(e: Expr) -> set:
    if isinstance(e, Leaf):
        return {e.name}
    if isinstance(e, App):
        out = set()
        for a in e.args:
            out |= fvs(a)
        return out
    if isinstance(e, Bin):
        return fvs(e.lhs) | fvs(e.rhs)
    if isinstance(e, Quant):
        return fvs(e.body) | set(e.binders)
    raise TypeError("unknown")
