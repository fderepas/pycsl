"""WL-04b — `List[<dataclass>]` PARAM element field read — **FIXED**.

Before the fix: a `List[Point]` param lowered to `array int` and `a[i].x` collapsed
to the opaque `get_x(a[i])` over an int element, so a concrete field property
`\result == a[i].x` was only re-expressible through the opaque getter (sound but
content-opaque; a fresh concrete field value was not provable). Verdict: UNPROVEN.

After the fix (wrong-lowering-to-fix.md §WL-04 record residual): a flat `List[Point]`
param is realized as `array point` (the record `point` emitted PURE — Why3 forbids a
mutable element inside `array`), so `a[i]` reads a real `point` and `a[i].x` projects
the faithful field. The true field property PROVES. Verdict: PROVEN."""
_ = 0
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i].x
def f(a: List[Point], i: int) -> int:
    return a[i].x
