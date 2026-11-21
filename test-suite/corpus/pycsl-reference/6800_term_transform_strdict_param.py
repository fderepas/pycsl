"""lv2 (driver run #3): a POSITIVE witness for the Term->Term transform recognizer's
READ-ONLY `Dict[str, str]` second parameter (the `proof2why3/canonical.py::substitute`
shape):

    def rename(t: T, m: Dict[str, str]) -> T:
        Var arm   -> Var(m.get(t.name, t.name))
        App arm   -> App(head=m.get(t.head, t.head), args=tuple(rename(a, m) for a in t.args))
        All arm   -> inner = {k: v for k, v in m.items() if k not in t.binders}
                     All(binders=t.binders, body=rename(t.body, inner))

The dict lowers to the ABSTRACT type `term__strdict`; `m.get(k, d)` to the
UNINTERPRETED `val function rename__get m k d` and the filtering comprehension to the
uninterpreted `val function rename__restrict m binders`. Both are deterministic in
their inputs (the body never mutates `m`), so every Python dict is a model: an
over-approximation, never an assumption; no axiom (ledger 3). Recursion is structural
over the certified `term` inductive (`variant { v_t }`), the `list term` child through
the element-wise `rename__list` map.

PROVES. The functions declare NO pre/postcondition (the recognizer gate admits only a
contract that claims nothing it would drop): the lock is the emission. Twin: 6801
(the same shape with `#@ ensures False`, expected FAIL).
"""
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
