"""Test 0474 — strings-plan demand-driver: __contains__ (`needle in haystack`).
Target: substring containment as a bool. The spec relates True to the existence of a
matching position (content reasoning — the hard SMT goal). Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(needle) <= \str_length(haystack)
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def contains(haystack: str, needle: str) -> bool:
    return needle in haystack
