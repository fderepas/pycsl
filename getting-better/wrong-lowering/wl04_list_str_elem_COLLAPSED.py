"""WL-04 COLLAPSED/WRONG-REPR — `List[str]` element read — **FIXED**.

Before the fix: `let f (a: array int) ... : string = a[i]` (a[i] : int vs return :
string) → INTERNALLY-INCONSISTENT, ill-typed WhyML (Detector D2: TYPEERR).

After the fix (wrong-lowering-to-fix.md §WL-04): a flat `List[str]` param is realized
as `array string`, so `a[i] : string` matches the `str` return — the WhyML type-checks
AND the faithful element read `\result == a[i]` is provable. Verdict: PROVEN."""
_ = 0
from typing import List


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i]
def f(a: List[str], i: int) -> str:
    return a[i]
