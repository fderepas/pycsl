"""WL-04a — `List[float]` LOCAL built by a LIST LITERAL — element read — **FIXED**.

Before: `a = [1.5, 2.5]; a[1]` folded to the int-truncated element `2` (an `int` vs
`real` collision against the `float` return — Detector D2: TYPEERR).

After (wrong-lowering-to-fix.md §WL-04a): the all-float literal is built as
`array real` and the indexed-read fold yields the faithful `2.5` — the fractional
value is preserved, never truncated. Verdict: PROVEN."""
_ = 0
from typing import List


#@ ensures \result == 2.5
def f() -> float:
    a = [1.5, 2.5]
    return a[1]
