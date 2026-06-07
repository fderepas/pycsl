"""Test 0617 — ref-wrapped array local dereferenced at the call site (07-1321 S2 regression).

A local built as a list literal then element-mutated is ref-wrapped; when passed to a callee it
must be dereferenced (`!x`), not passed as the ref cell. (Confirmed already correct in this tree;
pinned here against regression.)
"""
# pycsl-flags: --memory-model hoare


#@ requires \length(buf) >= 2
#@ ensures \result == buf[1]
#@ assigns \nothing
def helper(buf: list) -> int:
    return buf[1]


#@ ensures \result == 9
#@ assigns \nothing
def caller() -> int:
    x = [1, 2, 3]
    x[1] = 9
    return helper(x)
