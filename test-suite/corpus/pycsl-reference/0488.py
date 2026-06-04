"""Test 0488 — strings-plan demand-driver: __format__ (`format(s)`).
Target: format() with no spec is identity. (f-strings desugar through the same path; kept out
of the body since the parser front-end treats them separately.) Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == s
#@ assigns \nothing
def fmt0(s: str) -> str:
    return format(s)
