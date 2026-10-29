"""lv4 WITNESS (expected PASS): the AC-flatten-and-sort arm of a term transform (the
mirror's `proof2why3/canonical.py::_ac_normalize` shape; `_parse_ac_guard`).

`ac_norm`'s `Bin` arm for the `\\/` / `/\\\\` operators collects the maximal same-operator
operand chain through a NESTED `collect` (lifted by the front end, folded back into the
arm as a local structural `let rec`; the lifted sibling emits nothing), sorts the
normalized operands with `sorted(key=lambda x: x.pp())` (a defined stable insertion sort
over an uninterpreted key), and re-folds them right-leaning (`S[-1]`, `reversed(S[:-1])`).
The recursion `ac_norm(node)` is on a proper DESCENDANT of `t`, so it terminates by the
file's `term__size` measure (size mode, switched on by `sort_hyps` over `split_chain`):
the root call `collect(t)` takes its descent branch (`t.op == t.op`), every other call
carries the proved `term__size node < term__size t`. `S[-1]` is proved in range by the
sort's proved length law. Base: REFUSED (the lifted `collect` captures `operands`, `t`).
Controls: 7105 (`ensures False`, must NOT prove), 7106 (a closure that does not descend:
declined).
"""
# pycsl-expected: PASS
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
                collect(node.lhs)
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
