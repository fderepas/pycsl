r"""Test 4601 -- gen #37 route #339 (expected PASS): CONTROL: an `IntEnum` with no dunder keeps int semantics (`x - x == 0` under `no_exception \all` proves; CPython 0).
"""
# pycsl-expected: PASS
from enum import IntEnum

class P(IntEnum):
    LOW = 1
    HIGH = 2

    def next(self) -> int:
        return 0

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = P.LOW
    return x - x

if __name__ == "__main__":
    assert f() == 0
