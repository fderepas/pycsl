"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, T-transform):
a POSITIVE witness for the Term->Term (constructor-rebuild) transform algebra
over the class-instance VARIANT ADT.

A `\trusted`-free transform that isinstance-dispatches over a frozen-dataclass
UNION (`Expr = Leaf | Neg | Bin | Quant`) and RECONSTRUCTS a new Expr via the
variant constructors is lowered onto a total positional `match` over the Why3
VARIANT `term` that rebuilds terms:
  * an identity leaf arm (`return t`),
  * a single-ctor rebuild recursing on a term child (`Neg`),
  * a const-string-map conditional on a string field
    (`if e.op in _FLIP: return Bin(_FLIP[e.op], self(rhs), self(lhs))`) — the
    op-swap, lowered to a `pystr_eq` guard chain (result VC-free; ensures True),
  * the same-kind rebuild idiom (`kind = Forall if isinstance(e, Forall) else
    Exists; return kind(...)`) over Quant... (here a single Quant ctor with a
    list-string binder field + a term body).

PROVES — structurally terminating over the certified `term` inductive (co-landed
axiom-free with `Phase2i_TermIR.v` / `TermIR.lean`; ledger 3). A facade
regression (dropping a recursion, mis-copying the op map, or losing the arm-per-
constructor structure) changes this file's emission (the mutation-test /
vacuity-gate non-vacuity lock; the carrier forces `ensures True`, so there is no
postcondition evil-twin — exactly like the pyval walkers). The recognizer is
fail-closed + gated on `needs_term`, so every other corpus file emits
byte-identically.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Leaf:
    name: str


@dataclass(frozen=True)
class Neg:
    op: str
    arg: "Expr"


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "Expr"
    rhs: "Expr"


@dataclass(frozen=True)
class Quant:
    binders: tuple
    body: "Expr"


Expr = "Leaf | Neg | Bin | Quant"

_FLIP = {"<=": ">=", "<": ">"}


#@ requires True
#@ ensures True
#@ assigns \nothing
def flip(e: Expr) -> Expr:
    if isinstance(e, Leaf):
        return e
    if isinstance(e, Neg):
        return Neg(op=e.op, arg=flip(e.arg))
    if isinstance(e, Bin):
        if e.op in _FLIP:
            return Bin(_FLIP[e.op], flip(e.rhs), flip(e.lhs))
        return Bin(e.op, flip(e.lhs), flip(e.rhs))
    if isinstance(e, Quant):
        return Quant(binders=e.binders, body=flip(e.body))
    raise TypeError("unknown")
