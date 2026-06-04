"""Test 0504 — collections (negative): a false Counter contract must fail.

After a single `c[k] += 1` from the empty counter, `c[k] == 1`, not 2 — so `ensures \result == 2`
is UNPROVABLE. This confirms the Counter increment carries real content (a wrong count is
rejected by the prover), rather than an opaque stub under which the contract would vacuously
pass. Expected-FAIL = the postcondition does not discharge."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import Counter


#@ ensures \result == 2
def wrong_count() -> int:
    c = Counter()
    c[9] += 1
    return c[9]
