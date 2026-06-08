"""Test 0639 — a dynamic `exec` is a worst-case mutator: frame-taint (07-1839 P5a').

`exec(code)` can mutate arbitrary state, so in a frame-checked model (typed/store) it WRITES the heap.
A function that runs `exec` therefore cannot honestly claim `assigns \nothing` (whose typed-model
frame condition is `ensures !int_mem = old !int_mem`): the `exec_havoc … writes {int_mem}` op makes
that postcondition unprovable, so verification correctly FAILS. (Removing the exec line makes the
empty frame hold — the demonstration that exec is what taints the frame.)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed


#@ assigns \nothing
def f(code: str) -> int:
    exec(code)
    return 0
