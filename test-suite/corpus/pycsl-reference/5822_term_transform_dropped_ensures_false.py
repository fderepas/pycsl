"""levers-r3 SOUNDNESS WITNESS (expected FAIL) for the term-ADT recognizers'
contract gate (`generic_fold._term_contract_trivial`).

A Term->Term transform of the certified `_flip_comparisons` shape whose contract is
`#@ ensures False`. MEASURED at base `76537c560`: the transform recognizer emitted it
as `let rec iff_to_bin (v_t: term) : term ensures { true } variant { v_t } = match ...`
-- the declared postcondition DROPPED -- and the run printed `Verification SUCCESS! All
contracts formally proven.` for a claim no function can satisfy (a false proof).
With the gate, a recognizer fires only when every `ensures`/`requires` is the literal
`True` and no raises/no_exception claim is made; this file declines to the generic
lowering and must NOT prove. Control: 5820 (same shape, `ensures True`) PROVES.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class App:
    head: str
    args: tuple


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "T"
    rhs: "T"


@dataclass(frozen=True)
class Neg:
    arg: "T"


T = "Var | App | Bin | Neg"


#@ assigns \nothing
def has_var(t: T) -> bool:
    if isinstance(t, Var):
        return True
    if isinstance(t, App):
        return any(has_var(a) for a in t.args)
    if isinstance(t, Bin):
        return has_var(t.lhs) or has_var(t.rhs)
    if isinstance(t, Neg):
        return has_var(t.arg)
    raise TypeError("unknown")


#@ ensures False
#@ assigns \nothing
def iff_to_bin(t: T) -> T:
    if isinstance(t, Var):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(iff_to_bin(a) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, iff_to_bin(t.lhs), iff_to_bin(t.rhs))
    if isinstance(t, Neg):
        return Neg(iff_to_bin(t.arg))
    raise TypeError("unknown")
