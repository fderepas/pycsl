"""lv5 CONTROL (expected FAIL): 7230 WITHOUT `#@ requires len(counter) >= 1`. The
recognizer fires (requires `True`) and emits `requires { true }`, so the checked cell
reads `v_counter[0]` are unprovable: Python raises IndexError on an empty list once a
binder is reached. The precondition is load-bearing.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple


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
    lhs: "Term"
    rhs: "Term"


@dataclass(frozen=True)
class All:
    binders: tuple
    ty: str
    body: "Term"


@dataclass(frozen=True)
class Ex:
    binders: tuple
    ty: str
    body: "Term"


Term = "Var | App | Bin | All | Ex"


#@ assigns \nothing
def mk_chain(hyps: List[Term], conclusion: Term) -> Term:
    out: Term = conclusion
    for h in reversed(hyps):
        out = Bin("->", h, out)
    return out


#@ assigns \nothing
def split_chain(t: Term) -> Tuple[List[Term], Term]:
    hyps: List[Term] = []
    cur = t
    while isinstance(cur, Bin) and cur.op == "->":
        hyps.append(cur.lhs)
        cur = cur.rhs
    return hyps, cur


#@ assigns \nothing
def sort_hyps(t: Term) -> Term:
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
def subst(t: Term, m: Dict[str, str]) -> Term:
    if isinstance(t, Var):
        return Var(m.get(t.name, t.name))
    if isinstance(t, App):
        return App(head=t.head, args=tuple(subst(a, m) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, subst(t.lhs, m), subst(t.rhs, m))
    if isinstance(t, (All, Ex)):
        inner = {k: v for k, v in m.items() if k not in t.binders}
        kind = All if isinstance(t, All) else Ex
        return kind(binders=t.binders, ty=t.ty, body=subst(t.body, inner))
    raise TypeError("unknown")


#@ assigns counter
def rename(t: Term, counter: List[int]) -> Term:
    if isinstance(t, Var):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(rename(a, counter) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, rename(t.lhs, counter), rename(t.rhs, counter))
    if isinstance(t, (All, Ex)):
        new_names = []
        mapping: Dict[str, str] = {}
        for old in t.binders:
            new = f"v{counter[0]}"
            counter[0] += 1
            new_names.append(new)
            mapping[old] = new
        renamed = subst(t.body, mapping)
        renamed = rename(renamed, counter)
        kind = All if isinstance(t, All) else Ex
        return kind(binders=tuple(new_names), ty=t.ty, body=renamed)
    raise TypeError("unknown")


#@ assigns \nothing
def normalize(t: Term) -> Term:
    counter = [0]
    return rename(t, counter)
