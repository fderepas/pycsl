"""Test 0509 — dict boundary (negative): \length on a dict is unsupported.

A `dict`/`set` is modelled as a total `map int (option int)` with no cardinality, so `\length(d)`
is rejected at contract validation (a clear PyCSL error, not a cryptic Why3 `map`-vs-`array` type
mismatch). For key presence use `\has_key(d, k)`; for a length-bearing collection use a
list/array. Expected-FAIL = the validation rejects `\length` on the dict param (cf. 0199, which
demonstrates the supported dict-access subset)."""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires \length(d) >= 10
#@ ensures \result == d[0] + d[1]
def sum_first_two(d: dict) -> int:
    return d[0] + d[1]
