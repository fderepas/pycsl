"""Test 0485 — strings-plan demand-driver: __hash__ (`hash(s)`).
Target: hashing a string yields an int (usable as a dict/set key). Under the strings feature
hash becomes an abstract op over a Why3 string (vs the literal int-hash model today).
Expected-FAIL until strings land."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures True
#@ assigns \nothing
def shash(s: str) -> int:
    return hash(s)
