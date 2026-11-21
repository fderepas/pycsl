"""WL-04g false-twin (int+str) — a MIXED literal [1, "x"] must NOT prove any content
claim about the string element. If "x" coerces to its hash H, `a[1] == H` would PROVE
a claim meaningless in real Python. Verdict: must NOT be PROVEN."""
_ = 0
from typing import List


#@ ensures \result == 0
def f() -> int:
    a = [1, "x"]
    return a[1]
