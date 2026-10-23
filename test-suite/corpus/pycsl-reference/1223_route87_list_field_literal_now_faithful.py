"""Test 1223 — ROUTE #87's COMPLETENESS GAIN and its BOUNDING CONTROL.

The TRUE twin of 1222. Before the repair it was REFUSED while the FALSE claim proved; now the
field carries the same `let _alit = Array.make 3 (1) in _alit[1] <- 2; _alit[2] <- 3; _alit`
chain a LOCAL list literal has always produced, and this TRUE claim PROVES.

**WHY THE POSITIVE WITNESS IS LOAD-BEARING.** An over-broad repair — making every list field
unconstrained — would satisfy every expected-FAIL witness in this family at once while
destroying the capability. Only a file that must STILL PROVE can fail when the guard grows too
wide. 1211, 1215 and 1219 are the same instrument for routes #83, #79 and #85.

**IT ALSO PINS THE EMISSION'S UNIFORM-LITERAL CASE.** An ALL-EQUAL literal emits the plain
`(Array.make n v)` that the pre-repair emitter already produced, so the three REAL corpus files
that hold all-zero literals (0595, 0596, 0704) stay BYTE-IDENTICAL. That is not a trick to dodge
the byte-diff: `Array.make n v` IS the faithful lowering of a uniform literal, and choosing the
faithful form that coincides with the existing output is simply cheaper than paying for a
difference that carries no information.
"""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[0]
