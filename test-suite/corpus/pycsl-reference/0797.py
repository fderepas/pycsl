"""Test 0797 — nested list read is content-faithful (List[List[int]]).

nested-list.md S1-S3. A `List[List[int]]` param lowers to `array (seq int)`
(the Gate-B spike representation: outer `array`, inner PURE `seq`), so the inner
element `a[i]` is a real `seq int` and `a[i][j]` is a faithful `Seq.get` — not the
old opaque `int` collapse (nor the rectangular `matrix` model, which cannot even
express the per-row `len(a[i])`). So a driver can prove the two-index content
`\result == a[i][j]`. No new axiom (Seq read law is Why3 stdlib).
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == a[i][j]
def nested_read(a: List[List[int]], i: int, j: int) -> int:
    return a[i][j]

if __name__ == "__main__":
    assert nested_read([[1, 2], [3, 4, 5]], 1, 2) == 5
