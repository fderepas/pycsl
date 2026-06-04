"""Test 0486 — strings-plan demand-driver: __str__ (`str(s)`).
Target: str() of a str is the same string (identity). Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == s
#@ assigns \nothing
def tostr(s: str) -> str:
    return str(s)
