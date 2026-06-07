"""Test 0601 — negative: RETURNING an array of tuples is not yet supported (07-0903 W1 boundary).

Building and reading a list of tuples in a LOCAL is now supported (W1 — see 0607). But typing a
function that RETURNS one is not yet: the `-> list` annotation lowers to `array int`, while the
body builds an `array (int, int)` — a type mismatch. Returning (or passing) a tuple array needs
richer element-typed annotations (`List[Tuple[int, int]]`), a follow-on to W1. Until then this is
an honest hard error, NOT the old silent int-hash collapse.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \length(\result) == 2
#@ assigns \nothing
def pairs() -> list:
    return [(1, 2), (3, 4)]
