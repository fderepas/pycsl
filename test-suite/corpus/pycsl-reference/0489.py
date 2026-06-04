"""Test 0489 — strings-plan demand-driver: __iter__ (`for c in s`).
Target: iterating a string visits each character once; counting yields its length. Expected-FAIL
until strings land (and iteration over a string is supported)."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == \str_length(s)
#@ assigns \nothing
def count_iter(s: str) -> int:
    count = 0
    #@ loop invariant count >= 0
    #@ loop variant \str_length(s) - count
    for c in s:
        count = count + 1
    return count
