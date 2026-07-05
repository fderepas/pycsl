"""WL-03b false twin — the int-TRUNCATION claim of a `float` field slot.

This asserts something FALSE of real Python: that a `float` tuple slot / record field
holding `2.5` equals the truncated int value `2.0`. Under the (now-fixed) unsound int
collapse this would have been provable (the field was int, and `2.5` truncated to `2`);
under the faithful `real` model it is a false real claim (`2.5 <> 2.0`).

Soundness oracle: this driver MUST stay UNPROVEN. A PROVEN verdict would mean the float
field is still being truncated to int (the unsound collapse re-appeared)."""
_ = 0
from typing import Tuple
from dataclasses import dataclass


@dataclass
class P:
    n: int
    f: float


#@ requires t[1] == 2.5
#@ ensures \result == 2.0
def trunc_tuple_slot(t: Tuple[int, float]) -> float:
    return t[1]


#@ requires q.f == 2.5
#@ ensures \result == 2.0
def trunc_field(q: P) -> float:
    return q.f
