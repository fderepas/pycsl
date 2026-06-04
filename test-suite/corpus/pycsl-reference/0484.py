"""Test 0484 — strings-plan demand-driver: __mod__ (`s % x`, old-style formatting).
Target: %-formatting. Content of the result is NOT modeled (opaque) — this documents the
boundary; only that it produces a string. Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def fmt(s: str, x: int) -> str:
    return s % x
