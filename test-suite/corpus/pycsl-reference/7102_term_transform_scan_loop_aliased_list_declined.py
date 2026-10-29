"""lv4 SOUNDNESS WITNESS (expected FAIL, refused): the scan loop must not model a mutated
list that has an ALIAS. `keep = bs` makes `keep` the same list object as `bs`, so
`bs.extend(...)` also changes `keep` (the returned binders); a value model (a list is a
value) would return the un-extended tuple.
The scan arm requires every mutated list to be created by the block (`[]` / `list(..)`)
and never read before the loop, so this declines to the generic lowering, which refuses
`bs.extend(...)`. Control: 7100 (no alias) PROVES.
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


#@ assigns \nothing
def flat(t: T) -> T:
    if isinstance(t, All):
        nb = flat(t.body)
        bs = list(t.binders)
        keep = bs
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
        return All(binders=tuple(keep), ty=t.ty, body=out)
    if isinstance(t, Ex):
        return Ex(binders=t.binders, ty=t.ty, body=flat(t.body))
    if isinstance(t, Var):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(flat(a) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, flat(t.lhs), flat(t.rhs))
    raise TypeError("unknown")
