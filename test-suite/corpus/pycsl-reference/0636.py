"""Test 0636 — negative: \in_scope of a CONDITIONALLY-assigned local is withheld (07-1839 P3).

`z` is assigned only inside an `if` branch, so it is not bound on all paths → `\in_scope(z)` is
UNKNOWN (an uninterpreted bool), neither decided-true nor decided-false. Asserting it cannot be
proven — the definite-assignment guard refuses to certify membership on partial information (the
genuine unsoundness the old keys()-snapshot would have hit).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ ensures \in_scope(z)
#@ assigns \nothing
def f(x: int) -> int:
    if x > 0:
        z = 1
        return z
    return 0
