r"""Test 1311 — ROUTE #113 second carrier: a tuple-component PROJECTION returned from a try
(`return a[i][1]`) lowers to `(let (_, _r1_) = a[i] in _r1_)`, whose pattern comma made it "a
tuple"; it was replaced by a hash constant and `\result > 1000` PROVED for a component that is
20 or 40 (corpus 0607 passed on the same constant). The projection now passes through.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires 0 <= i and i < 2
#@ ensures \result > 1000
#@ assigns \nothing
def at_second(i: int) -> int:
    a = [(10, 20), (30, 40)]
    if a[i][0] >= 0:
        return a[i][1]
    return 5000
