"""Test 0804 — NEGATIVE: non-int-leaf in-place inner mutation is REJECTED.

nested-list-mutable.md boundary. In-place inner element mutation `a[i][j] = v` is
supported ONLY for a RECTANGULAR int leaf (`List[List[int]]` → the mutable
built-in `matrix int`). A NON-int leaf (`List[List[str]]`) has NO mutable 2-D
built-in — it stays on the read-only `array (seq string)` model, whose inner
`seq` is a PURE/immutable Why3 value. So an in-place inner mutation on it has no
sound WhyML rendering: the transpiler emits an assignment against the immutable
`seq` element, a HARD type/verification failure (`a[i]` is a `seq string`, not an
assignable cell). Rather than silently mis-model a shape/element change, the tool
REJECTS it. This test documents the boundary — mutable inner mutation is
int-leaf-only; ragged and `a[i].append(...)` (shape-change) mutation likewise stay
out of the mutable model (see nested-list-mutable.md §residual). The rectangular
int case IS faithful (0802/0803).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == 0
def bad_str_inner_mutate(a: List[List[str]], i: int, j: int, v: str) -> int:
    a[i][j] = v
    return 0
