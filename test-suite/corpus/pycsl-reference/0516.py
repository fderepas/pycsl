"""Test 0516 — referential transparency (negative): memoizing a non-RT function is rejected.

A `@lru_cache` function that is not established referentially transparent — here it lacks
`#@ assigns \nothing`, so it is not known to be effect-free — is rejected under UB-7.7: the cache
could return values inconsistent with the verified (uncached) body. Expected-FAIL = the pipeline
raises the UB-7.7 error rather than emitting an unsound proof."""
# pycsl-expected: FAIL
_ = 0  # anchor
from functools import lru_cache


#@ ensures \result == n
@lru_cache
def identity(n: int) -> int:
    return n
