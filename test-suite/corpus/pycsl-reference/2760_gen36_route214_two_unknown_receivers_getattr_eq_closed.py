r"""Test 2760 — route #214 CLOSED (expected FAIL): two `getattr` reads on DIFFERENT unknown receivers
with DIFFERENT attribute names used to share route #47's default-keyed constant, so `d == e` and
`\result == 0` PROVED while CPython answers 1. Closed by route #255 (323e857b: getattr over an erased
receiver is erased, and #249 makes `==` on erased values uninterpreted) -- bisected by the driver."""
# pycsl-expected: FAIL
from typing import Any

_ = 0  # anchor


#@ ensures \result == 0
def f(o: Any, p: Any) -> int:
    d = getattr(o, "a", {})
    e = getattr(p, "b", {})
    if d == e:
        return 0
    return 1


if __name__ == "__main__":
    class A:
        a = {1: 2}
    class B:
        b = {}
    print(f(A(), B()))
