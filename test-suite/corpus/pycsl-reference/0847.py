"""Test 0847 — float-leaf inner ELEMENT mutation a[i][j]=v reads back (POSITIVE).

wrong-lowering-to-fix.md §WL-04f (nested-inner-mutation). The real-leaf twin of 0804:
a `List[List[float]]` param that is IN-PLACE INNER-MUTATED lowers to `array (seq real)`
(outer array mutable, inner seq PURE) and the write lowers to the option-(c) store
`a[i] <- Seq.set a[i] j v`. So a driver proves the faithful real read-back
`(a[i][j] = v; a[i][j]) == v` — with the value carried as a Why3 `real` (τ(float)=real,
no int truncation). Also checks the outer/inner frame: a DISTINCT cell (i2, j2) keeps
its old real value after the write (the `Seq.set` frame + the untouched outer slot).
Both goals are Valid on Alt-Ergo and Z3; no new axiom.
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == v
def float_inner_mutate(a: List[List[float]], i: int, j: int, v: float) -> float:
    a[i][j] = v
    return a[i][j]

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ requires 0 <= i2 and i2 < len(a)
#@ requires 0 <= j2 and j2 < len(a[i2])
#@ requires i2 != i or j2 != j
#@ ensures \result == \old(a[i2][j2])
def float_inner_noalias(a: List[List[float]], i: int, j: int,
                        i2: int, j2: int, v: float) -> float:
    a[i][j] = v
    return a[i2][j2]

if __name__ == "__main__":
    m = [[1.5, 2.5], [3.5, 4.5, 5.5]]
    assert float_inner_mutate(m, 1, 2, 9.5) == 9.5
    assert m[1][2] == 9.5
    n = [[1.5, 2.5], [3.5, 4.5, 5.5]]
    assert float_inner_noalias(n, 0, 0, 1, 2, 9.5) == 5.5
