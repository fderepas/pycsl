r"""Test 5638 -- gen #37 route #397 (expected FAIL): `for self.k in [5]` in a dataclass `__post_init__`; `getattr(r, "k", 0) == 0`; PROVED at base 3b2d2e763 (CPython 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class R:
    x: int

    def __post_init__(self) -> None:
        for self.k in [5]:
            pass


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        print("result", f(R(1)))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
