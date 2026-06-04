"""Test 0483 — strings-plan demand-driver: __rmul__ (`n * s`, reflected repetition).
Target: integer-on-the-left repetition. Same semantics as __mul__. Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires n >= 0 and \str_length(s) >= 0
#@ ensures \str_length(\result) == n * \str_length(s)
#@ assigns \nothing
def rrep(n: int, s: str) -> str:
    return n * s
