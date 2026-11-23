r"""Test 10362 -- run #9 u65, route #620 (expected FAIL): red team rt75 F2 (probe c19). Method `C.m` is emitted as `let c__m`, the same WhyML name as the module-level `def c__m`. The emitter silently DROPPED the module-level definition, and the non-vacuity exemption of `-> NoReturn` functions (keyed by that name) exempted the VACUOUS method (its `requires` is x > 0 and x < 0): Verification SUCCESS on `\result == 99` (base b1400b11c). CPython: C().m(1) returns 1, VIOLATION of the claim. Now REFUSED (PYCSL-SEM-WHYML-NAME-CLASH): two definitions emitted under one WhyML name.
"""
# pycsl-expected: FAIL
from typing import NoReturn


def c__m(x: int) -> NoReturn:
    raise ValueError("x")


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ requires x > 0 and x < 0
    #@ ensures \result == 99
    def m(self, x: int) -> int:
        return 1


if __name__ == "__main__":
    r = C().m(1)
    print("VIOLATION contract" if r != 99 else "result", r)
