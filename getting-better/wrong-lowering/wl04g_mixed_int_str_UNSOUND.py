"""WL-04g UNSOUNDNESS PROBE (int+str) — the model hash-coerces "x" to 976090257 and
builds a WELL-TYPED `array int`. So `a[1] == 976090257` PROVES — but in real Python
`a[1]` is the STRING "x", NOT the int 976090257. A PROVEN here is SEVERITY-1 UNSOUND."""
_ = 0
from typing import List


#@ ensures \result == 976090257
def f() -> int:
    a = [1, "x"]
    return a[1]
