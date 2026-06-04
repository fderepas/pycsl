"""Test 0482 — strings-plan demand-driver: __mul__ (`s * n`, repetition).
Target: repetition multiplies the length. Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires n >= 0 and \str_length(s) >= 0
#@ ensures \str_length(\result) == n * \str_length(s)
#@ assigns \nothing
def rep(s: str, n: int) -> str:
    return s * n
