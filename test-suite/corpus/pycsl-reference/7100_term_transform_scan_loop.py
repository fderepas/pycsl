"""lv4 WITNESS (expected PASS): a term transform whose binder arm runs a `while True:`
SCAN loop down the term spine (the mirror's `proof2why3/canonical.py::_flatten_foralls`
shape; `scan` in `_parse_block_arm`). The loop extends a fresh `list(t.binders)` copy,
appends to a fresh `[]`, walks a look-ahead loop-local, and steps `cur = cur.body` /
`cur = cur.rhs` before every `continue`; it lowers to a local structural `let rec` over
the loop state (termination PROVED by `variant { s_cur }`), the list mutations to a
defined total append. Afterwards `if hyps: out = mk_chain(hyps, cur)` re-binds `out`.
Base: `flat` declines every term recognizer (generic lowering: `bs.extend(...)` REFUSED).
Control (expected FAIL): 7101 (`ensures False`).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


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
class All:
    binders: tuple
    ty: str
    body: "T"


@dataclass(frozen=True)
class Ex:
    binders: tuple
    ty: str
    body: "T"


T = "Var | App | Bin | All | Ex"


#@ assigns \nothing
def mk_chain(hyps: List[T], conclusion: T) -> T:
    out: T = conclusion
    for h in reversed(hyps):
        out = Bin("->", h, out)
    return out


#@ assigns \nothing
def flat(t: T) -> T:
    if isinstance(t, All):
        nb = flat(t.body)
        bs = list(t.binders)
        cur = nb
        hyps: List[T] = []
        while True:
            if isinstance(cur, All) and cur.ty == t.ty:
                bs.extend(cur.binders)
                cur = cur.body
                continue
            if isinstance(cur, Bin) and cur.op == "->":
                inner = cur.rhs
                while isinstance(inner, Bin) and inner.op == "->":
                    inner = inner.rhs
                if isinstance(inner, All) and inner.ty == t.ty:
                    hyps.append(cur.lhs)
                    cur = cur.rhs
                    continue
            break
        out = cur
        if hyps:
            out = mk_chain(hyps, cur)
        return All(binders=tuple(bs), ty=t.ty, body=out)
    if isinstance(t, Ex):
        return Ex(binders=t.binders, ty=t.ty, body=flat(t.body))
    if isinstance(t, Var):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(flat(a) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, flat(t.lhs), flat(t.rhs))
    raise TypeError("unknown")
