"""levers-r3 L-T1: a POSITIVE witness for the GUARDED constructor arm of the
Term->Term transform recognizer (the `proof2why3/canonical.py::_iff_app_to_binop`
shape):

    if isinstance(t, App) and t.head == "iff" and len(t.args) == 2:
        return Bin("iff", f(t.args[0]), f(t.args[1]))

placed BEFORE the general `App` arm. It lowers INSIDE the `App` match arm to
`if pystr_eq v_head "iff" then (match v_args with Cons g0 (Cons g1 Nil) -> Bin "iff"
(f g0) (f g1) | _ -> <general> end) else <general>`: `len(t.args) == 2` is exactly the
two-cons pattern, the string test is the VC-free `val pystr_eq` guard (the condmap
precedent — neither branch is assumed), and `g0`/`g1` are pattern-bound sub-terms so
the structural `variant` decreases. No new value shape, no axiom (ledger 3).

PROVES. The functions declare NO pre/postcondition (the recognizer gate admits only a
contract that claims nothing it would drop): the lock is the emission —
dropping the guard, the literal, the arity or an index changes this file's `.mlw`.
Twin: 5821 (a one-argument `not` guard rebuilding a `Neg`).
"""
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


#@ assigns \nothing
def iff_to_bin(t: T) -> T:
    if isinstance(t, App) and t.head == "iff" and len(t.args) == 2:
        return Bin("iff", iff_to_bin(t.args[0]), iff_to_bin(t.args[1]))
    if isinstance(t, Var):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(iff_to_bin(a) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, iff_to_bin(t.lhs), iff_to_bin(t.rhs))
    if isinstance(t, Neg):
        return Neg(iff_to_bin(t.arg))
    raise TypeError("unknown")
