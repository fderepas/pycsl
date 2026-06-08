"""Test 0637 — negative: \in_scope of a never-bound name is decided FALSE (07-1839 P3).

A name that is neither a parameter nor assigned anywhere in the body is not in local scope →
`\in_scope(nope)` lowers to `false`, so asserting it as a postcondition cannot hold.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ ensures \in_scope(nope)
#@ assigns \nothing
def f(x: int) -> int:
    return x
