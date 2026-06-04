"""Test 0476 — strings-plan demand-driver: __ne__ (`s != t`).
Target: content inequality. Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def strne(s: str, t: str) -> bool:
    return s != t
