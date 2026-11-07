"""WL-04g false-twin (int+float) — a MIXED literal [1, 2.5] must NOT prove a false
content claim. If `2.5` coerces to `2`, `a[1] == 2` would PROVE — a claim FALSE of
real Python (`a[1]` is `2.5`). That would be severity-1 UNSOUND. Verdict: must NOT
be PROVEN (UNPROVEN or REJECTED or TYPEERR)."""
_ = 0
from typing import List


#@ ensures \result == 2
def f() -> int:
    a = [1, 2.5]
    return a[1]
