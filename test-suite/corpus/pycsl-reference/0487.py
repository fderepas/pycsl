"""Test 0487 — strings-plan demand-driver: __repr__ (`repr(s)`).
Target: repr() adds surrounding quotes; the content transform is NOT modeled (opaque) — only
that repr is 2 chars longer than the value. Documents the boundary. Expected-FAIL."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) == \str_length(s) + 2
#@ assigns \nothing
def torepr(s: str) -> str:
    return repr(s)
