"""1191 — ROUTE #76 BOUNDARY CONTROL: a NamedTuple's `==` really IS structural.

This is what bounds route #76 and keeps it from being "object equality is unmodelled".
Python generates a STRUCTURAL `__eq__` for a NamedTuple (and for a `@dataclass` with the
default `eq=True`), so for those classes the model's structural `=` is FAITHFUL and must
keep proving. The defect is confined to classes whose `__eq__` is identity or user-written:
a plain class, a class defining its own `__eq__`, and `@dataclass(eq=False)`.

Same shape as route #59's List-vs-Dict control: two kinds of class have DIFFERENT equality
semantics in Python and the model gave both the same one. Measuring the faithful side is
what located the boundary rather than over-refusing everything.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import NamedTuple


class P(NamedTuple):
    v: int


#@ ensures \result == x
#@ assigns \nothing
def dup(x: P) -> P:
    return P(x.v)
