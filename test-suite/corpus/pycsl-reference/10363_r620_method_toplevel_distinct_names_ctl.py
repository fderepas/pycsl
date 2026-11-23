r"""Test 10363 -- run #9 u65, route #620 (expected PASS): over-refusal CONTROL. A module-level `-> NoReturn` function `c_m` (emitted `c_m`) beside method `C.m` (emitted `c__m`): the emitted WhyML names differ, so nothing is refused; the NoReturn function stays exempt from the non-vacuity gate, the method (a satisfiable `requires`) is probed and not vacuous, and its true claim proves.
"""
# pycsl-expected: PASS
from typing import NoReturn


def c_m(x: int) -> NoReturn:
    raise ValueError("x")


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ requires x > 0
    #@ ensures \result == x + 1
    def m(self, x: int) -> int:
        return x + 1


if __name__ == "__main__":
    r = C().m(4)
    try:
        c_m(1)
        print("VIOLATION contract: c_m returned")
    except ValueError:
        print("VIOLATION contract" if r != 5 else "result", r)
