"""WL-04a — `List[str]` LOCAL built by a LIST LITERAL — element read — **FIXED**.

Before: `a = ["x", "y", "z"]` lowered every element through `_coerce_to_int`, so
the literal emitted `Array.make 3 (976090257)` (hashed ints); `a[1] : int` collided
with the `str` return (Detector D2: TYPEERR).

After (wrong-lowering-to-fix.md §WL-04a): the all-string literal is built as
`array string` with the real string values, so `a[1] : string` matches the `str`
return and the faithful element read is provable. Verdict: PROVEN."""
_ = 0
from typing import List


#@ ensures \result == "y"
def f() -> str:
    a = ["x", "y", "z"]
    return a[1]
