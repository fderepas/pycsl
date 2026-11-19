"""lv2 SOUNDNESS WITNESS (expected FAIL): the read-only `Dict[str, str]` transform arm
of 6800 under a contract it cannot satisfy.

Same `rename(t, m)` as 6800, annotated `#@ ensures False`. The term recognizers emit a
fixed `ensures { true }`, so the fail-closed contract gate
(`generic_fold._term_contract_trivial`, route #420) must keep the new dict-parameter
path from firing: this file declines to the generic lowering and must NOT prove (a
`Verification SUCCESS` here would be a dropped-postcondition false proof).
Control: 6800 (same shape, no claim) PROVES.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class App:
    head: str
    args: tuple


@dataclass(frozen=True)
class Neg:
    arg: "T"


@dataclass(frozen=True)
class All:
    binders: tuple
    body: "T"


T = "Var | App | Neg | All"


#@ assigns \nothing
def has_var(t: T) -> bool:
    if isinstance(t, Var):
        return True
    if isinstance(t, App):
        return any(has_var(a) for a in t.args)
    if isinstance(t, Neg):
        return has_var(t.arg)
    if isinstance(t, All):
        return has_var(t.body)
    raise TypeError("unknown")


#@ ensures False
#@ assigns \nothing
def rename(t: T, m: Dict[str, str]) -> T:
    if isinstance(t, Var):
        return Var(m.get(t.name, t.name))
    if isinstance(t, App):
        return App(head=m.get(t.head, t.head), args=tuple(rename(a, m) for a in t.args))
    if isinstance(t, Neg):
        return Neg(rename(t.arg, m))
    if isinstance(t, All):
        inner = {k: v for k, v in m.items() if k not in t.binders}
        return All(binders=t.binders, body=rename(t.body, inner))
    raise TypeError("unknown")
