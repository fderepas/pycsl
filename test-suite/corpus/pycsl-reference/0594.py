"""Test 0594 — negative: a false fact about a `bytes` element is unprovable (0442.md B2).

Same `bytes`-as-`array int` model as `0593`, but the postcondition over-claims
`\result == buf[i] + 1` while the body returns `buf[i]`. The concrete array read makes the VC
refute it — confirming the byte buffer is modelled precisely, not as an opaque int.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \valid(buf, 4)
#@ requires 0 <= i and i < 4
#@ ensures \result == buf[i] + 1
#@ assigns \nothing
def at(buf: bytes, i: int) -> int:
    return buf[i]
