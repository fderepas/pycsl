"""WL-03b — a `float` record/tuple FIELD SLOT collapsed to `int` — **FIXED**.

Before the fix: the WL-03 synthesized per-slot record and the WL-04b `List[<record>]`
element/record models recognized slot/field types int/bool/str ONLY, so a `float`
field slot collapsed to `int`. A `Tuple[int, float]` slot read `t[1]` (or a
`@dataclass` `float` field `q.f`) truncated the fractional value: PyCSL read `2` where
real Python reads `2.5`. An UNSOUND int leak (τ(float)=real, no-more-int Stage D): the
faithful `\result == 2.5` law was UNPROVABLE / ill-typed against the int field.

After the fix (wrong-lowering-to-fix.md §WL-03b): a `float` field slot is realized as
Why3 `real` — in a synthesized `Tuple[int, float]` per-slot record (`field1: real`),
in a plain `@dataclass`/`self.f: float` record field, and in a `real`-field record used
as a `List[R]` element (emitted PURE — `real` is a pure type, so the record is legal at
an `array` element position). The projection `t[1]` / `q.f` / `a[i].f` reads the
faithful real, and the fractional value flows through. All three laws PROVE. Verdict:
PROVEN."""
_ = 0
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class P:
    n: int
    f: float


#@ requires t[1] == 2.5
#@ ensures \result == 2.5
def read_tuple_slot(t: Tuple[int, float]) -> float:
    return t[1]


#@ requires q.f == 2.5
#@ ensures \result == 2.5
def read_field(q: P) -> float:
    return q.f


#@ requires 0 <= i
#@ requires i < len(a)
#@ requires a[i].f == 2.5
#@ ensures \result == 2.5
def read_list_field(a: List[P], i: int) -> float:
    return a[i].f
