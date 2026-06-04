"""Test 0472 — strings-plan demand-driver: __len__ (`len(s)`).
Target: `len` on a runtime str returns its Why3 String.length. Expected-FAIL until the
strings feature lands (runtime str is an int hash today)."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == \str_length(s)
#@ assigns \nothing
def slen(s: str) -> int:
    return len(s)
