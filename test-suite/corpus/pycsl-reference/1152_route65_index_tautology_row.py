"""1152 — ROUTE #65 NEGATIVE: a trigger row whose condition is the literal `true`.

`("attr_call", "index") -> ("ValueError", "true")` was a self-described placeholder. `true`
discharges unconditionally, so the row had ZERO discrimination: `xs.index(5)` (absent,
CPython raises) and `xs.index(1)` (present, safe) gave IDENTICAL verdicts, both proving.
A row that looks like coverage and provides none is worse than a missing row.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ no_exception ValueError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return xs.index(5)
