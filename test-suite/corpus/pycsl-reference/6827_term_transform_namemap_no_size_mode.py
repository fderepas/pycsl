"""lv3 SOUNDNESS WITNESS (expected FAIL / refused): 6825's `norm_names` in a file
WITHOUT the `term__size` measure.

`norm_names` recurses on `br = subst(t.body, m) if m else t.body`, which is not a
subterm; its termination rests on the file's proved size measure and `subst`'s proved
size postcondition, both of which exist only in size mode (switched on by a
flatten-recursing transform, `sort_hyps` in 6825). Here `sort_hyps` is absent, so the
namemap path must decline (fail closed) and the function keeps the generic lowering.
Control: 6825 (size mode on) PROVES.
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
