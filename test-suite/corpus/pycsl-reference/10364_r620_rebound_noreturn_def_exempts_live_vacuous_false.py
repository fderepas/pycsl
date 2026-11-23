r"""Test 10364 -- run #9 u65, route #620 (b) (expected FAIL): the module-level name `f` is bound twice. The FIRST `def f` is `-> NoReturn` (an annotation, not a `#@` claim, so route #463 admits the rebinding) and the LIVE second `def f` has a contradictory `requires` (x > 0 and x < 0) and claims `\result == 99`. The model keeps the live def, but the non-vacuity exemption set (keyed by the WhyML name `f`) took the dead NoReturn binding's flag and skipped the vacuous live def's probe. CPython: f(1) returns 1, VIOLATION of the claim. Now an exempt name that more than one definition maps to is never exempted: FAILED (vacuous `f`).
"""
# pycsl-expected: FAIL
from typing import NoReturn


def f(x: int) -> NoReturn:
    raise ValueError("x")


#@ requires x > 0 and x < 0
#@ ensures \result == 99
def f(x: int) -> int:
    return 1


if __name__ == "__main__":
    r = f(1)
    print("VIOLATION contract" if r != 99 else "result", r)
