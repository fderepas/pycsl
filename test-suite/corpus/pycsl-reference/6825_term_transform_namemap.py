"""lv3 WITNESS (expected PASS): a 1-param term transform that CALLS a `(str) -> str`
function on its string fields and renames its binder arm through a read-only
`Dict[str, str]` transform (the mirror's `proof2why3/canonical.py::_normalize_names`
shape; `_recognize_term_transform_namemap`).

`norm_names` rebuilds every constructor: `Var(snake(t.name))`, `App(head=snake(t.head),
args=tuple(norm_names(a) for a in t.args))`, and in the binder arm
`nb = tuple(snake(b) for b in t.binders)`, `m = {o: w for o, w in zip(t.binders, nb) if
o != w}`, `br = subst(t.body, m) if m else t.body`, `kind(binders=nb, ty=snake(t.ty),
body=norm_names(br))`. The recursion on `br` is NOT on a subterm: it terminates by the
file's `term__size` measure (size mode, switched on by `sort_hyps` over `split_chain`)
and the PROVED postcondition of `subst` that renaming preserves the size. The dict is
abstract (`zipmap` / `nonempty` uninterpreted, no axiom).
Base: `norm_names` declines every older term recognizer (generic lowering, REFUSED).
Controls: 6826 (`ensures False`, must NOT prove), 6827 (no size mode: declined).
"""
# pycsl-expected: PASS
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
def subst(t: T, m: Dict[str, str]) -> T:
    if isinstance(t, Var):
        return Var(m.get(t.name, t.name))
    if isinstance(t, App):
        return App(head=m.get(t.head, t.head), args=tuple(subst(a, m) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, subst(t.lhs, m), subst(t.rhs, m))
    if isinstance(t, (All, Ex)):
        inner = {k: v for k, v in m.items() if k not in t.binders}
        kind = All if isinstance(t, All) else Ex
        return kind(binders=t.binders, ty=t.ty, body=subst(t.body, inner))
    raise TypeError("unknown")


#@ assigns \nothing
def snake(name: str) -> str:
    return name.lower()


#@ assigns \nothing
def norm_names(t: T) -> T:
    if isinstance(t, Var):
        return Var(snake(t.name))
    if isinstance(t, App):
        return App(head=snake(t.head), args=tuple(norm_names(a) for a in t.args))
    if isinstance(t, Bin):
        return Bin(t.op, norm_names(t.lhs), norm_names(t.rhs))
    if isinstance(t, (All, Ex)):
        nb = tuple(snake(b) for b in t.binders)
        mapping = {old: new for old, new in zip(t.binders, nb) if old != new}
        br = subst(t.body, mapping) if mapping else t.body
        ty2 = snake(t.ty)
        kind = All if isinstance(t, All) else Ex
        return kind(binders=nb, ty=ty2, body=norm_names(br))
    raise TypeError("unknown")
