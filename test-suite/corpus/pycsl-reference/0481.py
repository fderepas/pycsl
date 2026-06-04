"""Test 0481 — strings-plan demand-driver: __add__ (`s + t`, concatenation).
Target: `+` on runtime str is concat (today it is nonsensical int-add). Length is additive.
Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0 and \str_length(t) >= 0
#@ ensures \str_length(\result) == \str_length(s) + \str_length(t)
#@ ensures \result == s ^ t
#@ assigns \nothing
def cat(s: str, t: str) -> str:
    return s + t
