"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, T-string):
a POSITIVE witness for the term->string BUILD catamorphism over the
class-instance VARIANT ADT (the `_pp`/pretty-print family).

A `\trusted`-free string-returning fold that isinstance-dispatches over a
frozen-dataclass UNION (`T = Var | Num | Flag | App | Bin | Quant`) and BUILDS a
string per arm — via f-string, `str()` (int->string), `" ".join` over a
list-string binder field, and `" ".join(pp(a, ...) for a in t.args)` over a
list-term App-arg field (the recursion that makes it a catamorphism) — while
threading a second inherited-attribute `parent_prec: int` that drives a
precedence-table lookup (`_OPPREC.get(op, default)`), int arithmetic
(`op_prec + 1`) and a conditional paren-wrap (`f"({s})" if parent_prec > p`).

It lowers onto a PROGRAM `let rec pp (v_t: term) (parent_prec: int) : string`
that is a total positional `match` over the Why3 VARIANT `term` — structurally
terminating over the certified `term` inductive (co-landed axiom-free with
`Phase2i_TermIR.v` / `TermIR.lean`; ledger 3), with an inline `pp__joinstr`
(list-string space-join), a mutual `pp__joinargs` (term-list `pp` join), and a
`pp__binop_prec__OPPREC` int table (the str->int const dict, `val pystr_eq`
string guard — a `val`, NOT an axiom). `has_var` seeds the constructor set.

PROVES. A facade regression (dropping a recursion, mis-copying a separator or the
precedence table, or losing the arm-per-constructor structure) changes this
file's emission (the mutation-test / vacuity-gate non-vacuity lock; the carrier
forces `ensures True`, so there is no postcondition evil-twin — exactly like the
pyval walkers). The 0959 twin (separator ` . ` -> ` ; `) is byte-different here.
The recognizer is fail-closed + gated on `needs_term`, so every other corpus
file emits byte-identically.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Num:
    value: int


@dataclass(frozen=True)
class Flag:
    value: bool


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
class Quant:
    binders: tuple
    body: "T"


T = "Var | Num | Flag | App | Bin | Quant"

_PREC_TOP = 0
_PREC_CMP = 4
_PREC_APP = 7
_PREC_ATOM = 8
_OPPREC = {"->": 1, "\\/": 2}


#@ requires True
#@ ensures True
#@ assigns \nothing
def has_var(t: T) -> bool:
    if isinstance(t, Var):
        return True
    if isinstance(t, (Num, Flag)):
        return False
    if isinstance(t, App):
        return any(has_var(a) for a in t.args)
    if isinstance(t, Bin):
        return has_var(t.lhs) or has_var(t.rhs)
    if isinstance(t, Quant):
        return has_var(t.body)
    raise TypeError("unknown")


#@ requires True
#@ ensures True
#@ assigns \nothing
def pp(t: T, parent_prec: int) -> str:
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Num):
        return str(t.value)
    if isinstance(t, Flag):
        return "true" if t.value else "false"
    if isinstance(t, Quant):
        binders = " ".join(t.binders)
        body = pp(t.body, _PREC_TOP)
        s = f"forall {binders} ; {body}"
        return f"({s})" if parent_prec > _PREC_TOP else s
    if isinstance(t, Bin):
        op_prec = _OPPREC.get(t.op, _PREC_CMP)
        if t.op == "->":
            lhs = pp(t.lhs, op_prec + 1)
            rhs = pp(t.rhs, op_prec)
        else:
            lhs = pp(t.lhs, op_prec)
            rhs = pp(t.rhs, op_prec + 1)
        s = f"{lhs} {t.op} {rhs}"
        return f"({s})" if parent_prec > op_prec else s
    if isinstance(t, App):
        if not t.args:
            return t.head
        args_s = " ".join(pp(a, _PREC_ATOM) for a in t.args)
        s = f"{t.head} {args_s}"
        return f"({s})" if parent_prec > _PREC_APP else s
    raise TypeError("unknown")
