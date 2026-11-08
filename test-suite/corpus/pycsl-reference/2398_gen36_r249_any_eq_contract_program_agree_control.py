r"""Test 2398 — route #249 (expected PASS): CONTROL: one uninterpreted `pycsl_py_eq` serves contract and program, so a program test and a
clause over the SAME operands agree: `if x == y: return 1` PROVES `ensures x == y ==> \result == 1`
(no law of `==` is used; `__eq__` is taken to be deterministic).
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures x == y ==> \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x == y:
        return 1
    return 0


if __name__ == "__main__":
    class A:
        def __eq__(self, o: object) -> bool:
            return True

        def __hash__(self) -> int:
            return 0

    class B:
        def __eq__(self, o: object) -> bool:
            return False

        def __hash__(self) -> int:
            return 0

    assert f(A(), B()) == 1 and f(1, 1) == 1
