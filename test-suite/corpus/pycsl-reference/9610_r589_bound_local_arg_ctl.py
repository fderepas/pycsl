r"""Test 9610 -- route #589 CONTROL (expected PASS, the advice of PYCSL-R589 followed): the operand is bound to a local in a plain statement first (`v = xs[0]`, its bound obligation discharged by the precondition), then passed as the second constructor argument. The handler path computes the result from `v`.
"""
# pycsl-expected: PASS
from typing import List


class E(Exception):
    pass


#@ requires len(xs) >= 1
#@ no_exception \all
#@ ensures \result == xs[0] + 1
def f(xs: List[int]) -> int:
    v = xs[0]
    try:
        raise E("a", v)
    except E:
        return v + 1
    return 0


if __name__ == "__main__":
    print(f([4]))
