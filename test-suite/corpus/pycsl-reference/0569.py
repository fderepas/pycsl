"""Test 0569 — negative: bounded-set universal without the membership hypothesis.

Same as 0568 but WITHOUT `requires k in s`. `\result == k` and the bound says only
that *members* of `s` are non-negative — with no proof that `k` is a member, `k >= 0`
does not follow. Demonstrates the membership guard (`k in s`) is load-bearing for the
instantiation in 0568.

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \forall x: int in s; x >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def pick(s: set, k: int) -> int:
    return k
