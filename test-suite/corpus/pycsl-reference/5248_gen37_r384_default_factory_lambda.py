r"""Test 5248 -- gen #37 route #384 (expected FAIL): `@dataclass` list field `default_factory=lambda: [0]` under `\length >= 2`: no goal, assumed; now REFUSED (R384; CPython IndexError). PROVED at base 0a2d8019b.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


#@ class invariant \length(self.xs) == 5
@dataclass
class D:
    xs: List[int] = field(default_factory=lambda: [0] * 4)

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.xs[4]


if __name__ == "__main__":
    try:
        D().last()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
