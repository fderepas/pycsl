"""WL-04b — same defect for `List[float]` — **FIXED**.

Before the fix: `let f (a: array int) ... : real = a[i]` (a[i] : int vs return : real)
→ ill-typed WhyML (Detector D2: TYPEERR).

After the fix (wrong-lowering-to-fix.md §WL-04): a flat `List[float]` param is realized
as `array real`, so `a[i] : real` matches the `float` return — the WhyML type-checks AND
the faithful element read `\result == a[i]` is provable. Verdict: PROVEN."""
_ = 0
from typing import List


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i]
def f(a: List[float], i: int) -> float:
    return a[i]
