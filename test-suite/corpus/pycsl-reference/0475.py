"""Test 0475 — strings-plan demand-driver: __eq__ (`s == t`, content equality).
Target: content equality replacing the unsound int-hash identity. Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def streq(s: str, t: str) -> bool:
    return s == t
