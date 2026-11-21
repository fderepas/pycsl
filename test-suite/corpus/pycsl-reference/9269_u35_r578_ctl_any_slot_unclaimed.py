r"""Test 9269 -- route #578 CONTROL (expected PASS at base and HEAD): route #252's obligation is an EXCEPTION site, so it is
placed only under a `no_exception` claim: the `Any` slot read `t[1] == k` / `t[1] is None` and `x & 1` on `x: Any` in a function
WITHOUT such a claim keep verifying (no law is used; the claims do not depend on the `Any` value).
"""
# pycsl-expected: PASS
from typing import Any, Tuple


def g(k: int) -> Tuple[int, Any]:
    return (1, None)


#@ ensures \result == 1
def f1(k: int) -> int:
    t = g(k)
    if t[1] is None:
        return 1
    return 1


#@ requires k >= 0
#@ ensures \result == k
def f2(x: Any, k: int) -> int:
    v = x & 1
    r = 0
    if k > 0:
        r = k
    return r


if __name__ == "__main__":
    print(f1(1), f2(3, 1))
