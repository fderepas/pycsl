"""Test 0473 — strings-plan demand-driver: __getitem__ slicing (`s[a:b]`).
Target: a slice is a substring of the stated length. Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires 0 <= a and a <= b and b <= \str_length(s)
#@ ensures \str_length(\result) == b - a
#@ ensures \result == \str_sub(s, a, b)
#@ assigns \nothing
def substr(s: str, a: int, b: int) -> str:
    return s[a:b]
