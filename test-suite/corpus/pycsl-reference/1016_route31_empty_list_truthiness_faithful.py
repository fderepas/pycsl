"""Test 1016 — ROUTE #31 POSITIVE witness: the faithful truthiness of an empty
and of a non-empty list local.

`[]` is falsy and `[7]` is truthy, so Python returns 2 then 1. Both are now
provable — route #31 was closed as a CAPABILITY, not merely as a refusal: the
model reads the same statically-known literal size that `len()` folds against,
and the sidecar `X_len` ref for an append target.

The companion of 1015, which is the same first function with a contract that is
FALSE of it.
"""
_ = 0  # anchor
#@ ensures \result == 2
#@ assigns \nothing
def f_empty() -> int:
    a = []
    if a:
        return 1
    return 2


#@ ensures \result == 1
#@ assigns \nothing
def f_nonempty() -> int:
    a = [7]
    if a:
        return 1
    return 2
