r"""Test 5100 -- gen #37 route #226 increment 2c (expected FAIL): the registered carrier. `#@ class invariant \length(self.xs) >= 1` over a LIST field bound to an `__init__` parameter, no `#@ requires`; the invariant was ASSUMED (no constructor goal), so `#@ no_exception \all` on `self.xs[0]` PROVED. CPython `D([]).first()` raises IndexError. 2c states `forall xs : array int. xs = xs -> (Array.length xs >= 1)`, which FAILS.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.xs) >= 1
@mutable_state
class D:
    def __init__(self, xs: List[int]) -> None:
        self.xs = xs

    #@ no_exception \all
    #@ assigns \nothing
    def first(self) -> int:
        return self.xs[0]


if __name__ == "__main__":
    try:
        D([]).first()
        raise SystemExit("expected IndexError")
    except IndexError:
        print("IndexError")
