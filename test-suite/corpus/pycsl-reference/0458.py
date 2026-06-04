"""Test 0458 — a false `#@ assert` must FAIL (the obligation has teeth).

`requires x > 0` does not imply `x > 100`, so the mid-body assert is unprovable
and verification fails. This proves `#@ assert` is a real proof obligation, not
the no-op Python `assert`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x > 0
def gap(x: int) -> int:
    #@ assert x > 100
    return x
