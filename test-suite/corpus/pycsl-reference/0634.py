"""Test 0634 — negative: isinstance on an Any-typed operand stays SYMBOLIC (07-1839 P4 / B).

An unannotated parameter has τ = Any → no decided tag (decision B), so `\typeof` is a free symbolic
tag and `isinstance(x, int)` is neither provable nor refutable. Asserting it cannot be proven.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ ensures isinstance(x, int)
#@ assigns \nothing
def f(x) -> int:
    return 0
