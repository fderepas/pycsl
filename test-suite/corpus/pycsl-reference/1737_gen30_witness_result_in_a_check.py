r"""Test 1737 — WITNESS for `PYCSL-SEM-CHECKPOINT`: `\result` inside a statement-level
`#@ check`.

`\result` is bound only at return, so naming it mid-body is meaningless — the refusal says
to use `ensures` for a claim about the returned value. One of the unwitnessed refusals
measured by `bin/check-refusal-witness-coverage.py`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == n
def f(n: int) -> int:
    #@ check \result == n
    return n
