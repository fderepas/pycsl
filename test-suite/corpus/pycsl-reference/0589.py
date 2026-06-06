"""Test 0589 — negative: `zfill(30)` does NOT establish length >= 31 (1009.md R2).

Same shape as `0588` but the consumer requires `\valid(b, 31)` (`Array.length b >= 31`). The
pad method only guarantees `Array.length result >= 30` (the width `x0`), so the precondition
is unprovable. Confirms the R2 length bound is exactly the width — sound and precise, not an
over-claim that would let any downstream `\valid` slip through.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \valid(b, 31)
#@ ensures \result == b[0]
#@ assigns \nothing
def needs31(b: list) -> int:
    return b[0]


#@ assigns \nothing
def run(name: str) -> int:
    padded = name.encode('utf-8').zfill(30)
    return needs31(padded)
