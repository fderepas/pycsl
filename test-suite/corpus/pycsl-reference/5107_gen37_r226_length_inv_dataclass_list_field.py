r"""Test 5107 -- gen #37 route #226 increment 2c (expected FAIL): a `@dataclass` with a `List[int]` field under `\length(self.xs) >= 1`. The SYNTHESIZED `__init__` binds `xs` from a parameter and has no contract, so the goal is premise-free and FAILS. At base `#@ no_exception \all` on `self.xs[0]` PROVED; CPython `D([]).first()` raises IndexError.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List


#@ class invariant \length(self.xs) >= 1
@dataclass
class D:
    xs: List[int]

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
