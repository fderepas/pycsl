"""lv4 SOUNDNESS WITNESS (expected FAIL, refused): a `collect` closure that recurses on
`node` ITSELF (`collect(node)`) instead of its sub-terms loops forever in Python. The AC
arm accepts only recursion on term FIELDS of the narrowed node, so this declines (the
lifted `collect` is then refused). Control: 7104 PROVES.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Var:
    name: str

    def pp(self) -> str:
        return self.name


@dataclass(frozen=True)
class App:
    head: str
    args: tuple

    def pp(self) -> str:
        return self.head


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "T"
    rhs: "T"

    def pp(self) -> str:
        return self.op


@dataclass(frozen=True)
class All:
    binders: tuple
    ty: str
    body: "T"

    def pp(self) -> str:
        return self.ty


@dataclass(frozen=True)
class Ex:
    binders: tuple
    ty: str
    body: "T"

    def pp(self) -> str:
        return self.ty


T = "Var | App | Bin | All | Ex"


#@ assigns \nothing
def mk_chain(hyps: List[T], conclusion: T) -> T:
    out: T = conclusion
    for h in reversed(hyps):
        out = Bin("->", h, out)
    return out


#@ assigns \nothing
def split_chain(t: T) -> Tuple[List[T], T]:
    hyps: List[T] = []
    cur = t
    while isinstance(cur, Bin) and cur.op == "->":
        hyps.append(cur.lhs)
        cur = cur.rhs
    return hyps, cur


#@ assigns \nothing
def sort_hyps(t: T) -> T:
    if isinstance(t, Bin) and t.op == "->":
        hyps, conclusion = split_chain(t)
        hn = [sort_hyps(h) for h in hyps]
        cn = sort_hyps(conclusion)
        return mk_chain(hn, cn)
    if isinstance(t, Var):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(sort_hyps(a) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, sort_hyps(t.lhs), sort_hyps(t.rhs))
    if isinstance(t, (All, Ex)):
        kind = All if isinstance(t, All) else Ex
        return kind(binders=t.binders, ty=t.ty, body=sort_hyps(t.body))
    raise TypeError("unknown")


#@ assigns \nothing
def ac_norm(t: T) -> T:
    if isinstance(t, Bin) and t.op in ("\\/", "/\\\\"):
        operands: List[T] = []

        def collect(node: T) -> None:
            if isinstance(node, Bin) and node.op == t.op:
                collect(node)
                collect(node.rhs)
            else:
                operands.append(ac_norm(node))

        collect(t)
        operands_sorted = sorted(operands, key=lambda x: x.pp())
        out = operands_sorted[-1]
        for o in reversed(operands_sorted[:-1]):
            out = Bin(t.op, o, out)
        return out
    if isinstance(t, Var):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(ac_norm(a) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, ac_norm(t.lhs), ac_norm(t.rhs))
    if isinstance(t, (All, Ex)):
        kind = All if isinstance(t, All) else Ex
        return kind(binders=t.binders, ty=t.ty, body=ac_norm(t.body))
    raise TypeError("unknown")
