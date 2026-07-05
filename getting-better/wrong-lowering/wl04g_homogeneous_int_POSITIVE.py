"""WL-04g positive regression — a HOMOGENEOUS all-int list literal is UNAFFECTED by
the mixed-literal reject guard: it still builds `array int` and proves. Guards
against over-rejection. Verdict: PROVEN."""
_ = 0
from typing import List


#@ ensures \result == 20
def f() -> int:
    a = [10, 20, 30]
    return a[1]
