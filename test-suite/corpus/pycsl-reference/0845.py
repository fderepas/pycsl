"""Test 0845 — WL-03b regression lock (POSITIVE): a `float` record/tuple FIELD SLOT is
the faithful Why3 `real`, not the int collapse.

The WL-03 synthesized per-slot record and the WL-04b `List[<record>]` element/record
models recognized slot/field types int/bool/str ONLY, so a `float` field slot collapsed
to `int` — an UNSOUND leak that truncated a fractional read (`t[1]` / `q.f` / `a[i].f`
holding `2.5` read `2`). WL-03b realizes a `float` field slot as `real` (τ(float)=real,
no-more-int Stage D):

  * a recognized `Tuple[int, float]` synthesizes `pytuple_int_real = { field0: int;
    field1: real }`, so `t[1]` projects the REAL slot;
  * a `@dataclass P: n: int; f: float` (and a `self.f: float` field) emits `f: real`;
  * a `real`-field record used as a `List[P]` element is emitted PURE (`real` is a pure
    type — legal at an `array` element position), so `a[i].f` projects the real field.

Each function reads the fractional value faithfully — proving the `\result == 2.5` law
that was UNPROVABLE / ill-typed against the int field. The NEGATIVE twin is 0846.
"""
_ = 0  # anchor
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class P:
    n: int
    f: float


#@ requires t[1] == 2.5
#@ ensures \result == 2.5
def read_tuple_slot(t: Tuple[int, float]) -> float:
    """`Tuple[int, float]` slot read at real — the float slot is `field1: real`."""
    return t[1]


#@ requires q.f == 2.5
#@ ensures \result == 2.5
def read_field(q: P) -> float:
    """A plain record-param float field read at real."""
    return q.f


#@ requires 0 <= i
#@ requires i < len(a)
#@ requires a[i].f == 2.5
#@ ensures \result == 2.5
def read_list_field(a: List[P], i: int) -> float:
    """A `List[P]` element's float field read at real (PURE-element record)."""
    return a[i].f


if __name__ == "__main__":
    assert read_tuple_slot((1, 2.5)) == 2.5
    assert read_field(P(0, 2.5)) == 2.5
    assert read_list_field([P(0, 2.5)], 0) == 2.5
