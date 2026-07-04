"""Test 0803 — in-place inner mutation is NON-ALIASING (POSITIVE).

nested-list-mutable.md. Over the mutable `matrix int` model (the representation
an inner-mutated `List[List[int]]` routes to), an update at cell (i,j) leaves any
DISTINCT cell (i2,j2) unchanged — `Matrix.set` writes exactly one element. So a
driver can prove that after `a[i][j] = v`, the read `a[i2][j2]` (with
(i2,j2) != (i,j)) equals its OLD value. This is the frame/non-aliasing law that
makes the mutable nested model usable — a mutation does not silently perturb the
rest of the matrix. The Gate-B spike (spikes/nested-list-mutable.mlw,
`m_update_noalias`) proved it Valid in both Alt-Ergo and Z3. No new axiom (the
`Matrix.set` frame `a.elts = (old a.elts)[r <- (old a.elts r)[c <- v]]` is Why3
stdlib).
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ requires 0 <= i2 and i2 < len(a)
#@ requires 0 <= j2 and j2 < len(a[i2])
#@ requires i2 != i or j2 != j
#@ ensures \result == \old(a[i2][j2])
def mutate_noalias(a: List[List[int]], i: int, j: int,
                   i2: int, j2: int, v: int) -> int:
    a[i][j] = v
    return a[i2][j2]

if __name__ == "__main__":
    m = [[1, 2, 3], [4, 5, 6]]
    assert mutate_noalias(m, 0, 0, 1, 2, 99) == 6
