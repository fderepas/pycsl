"""Test 0848 — NEGATIVE false twin of 0804: post-mutation cell is NOT != v.

wrong-lowering-to-fix.md §WL-04f (nested-inner-mutation). Soundness oracle for the
option-(c) inner-mutation store `a[i][j] = v ~~> a[i] <- Seq.set a[i] j v`. After the
write the cell (i, j) holds EXACTLY `v`, so a claim that the read-back is DIFFERENT
from `v` is false of real Python and MUST stay UNPROVEN. If this ever PROVES, the
functional `Seq.set` update is not being stored back into the mutable outer array
(the write is being dropped / mis-modelled), i.e. the mutation lowering is unsound.

Mirrors the Gate-B spike's `m_update_falsetwin` goal (Timeout/Unknown = correctly
unproven on both provers).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result != v
def str_inner_mutate_falsetwin(a: List[List[str]], i: int, j: int, v: str) -> str:
    a[i][j] = v
    return a[i][j]

if __name__ == "__main__":
    m = [["a", "b", "c"], ["d", "e", "f"]]
    assert str_inner_mutate_falsetwin(m, 1, 2, "Z") == "Z"  # read-back IS "Z" — contract claims != "Z", FALSE
