"""WL-04b — `List[Tuple[int, str]]` PARAM element slot read — **FIXED**.

Before the fix: a `List[Tuple[int, str]]` param with `a[i][1]` was hijacked into the
rectangular `matrix int` model or collapsed through `subscript_get a[i] 1` (an int at
a `str` use site) — internally inconsistent, ill-typed WhyML. Verdict: TYPEERR.

After the fix (wrong-lowering-to-fix.md §WL-04 record residual): the WL-03 per-slot
record `pytuple_int_str` is reused as the list ELEMENT (`array pytuple_int_str`, the
record emitted PURE), so `a[i]` reads the tuple record and `a[i][1]` projects the
STRING slot `field1` at its faithful type. Verdict: PROVEN."""
_ = 0
from typing import List, Tuple


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i][1]
def f(a: List[Tuple[int, str]], i: int) -> str:
    return a[i][1]
