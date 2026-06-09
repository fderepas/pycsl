"""Test 0690 — negative: undefined variable inside a quantifier body.

Inside `\forall k; ... a[k] > nope`, the binder `k` is bound (not flagged) and `a`/`n`
are params, but `nope` is undefined. Gates the IR free-variable extraction's binder
exclusion + body recursion (core_ir_semantic._ir_free_vars). Phase B.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires \forall k; 0 <= k and k < n ==> a[k] > nope
def f(a: list, n: int) -> int:
    return 0
