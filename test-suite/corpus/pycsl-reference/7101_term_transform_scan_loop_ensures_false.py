"""lv4 SOUNDNESS WITNESS (expected FAIL): 7100's `flat` under `#@ ensures False`.

The term recognizers emit a fixed `ensures { true }`; the fail-closed contract gate
(`_term_contract_trivial`) must keep the new scan-loop arm from firing on a function that
claims something, so this file declines to the generic lowering and must NOT prove.
Control: 7100 (same function, no claim) PROVES.
"""
# pycsl-expected: FAIL
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


#@ ensures False
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
