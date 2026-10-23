r"""Test 2308 — gen #36 r243 (expected FAIL): route #243: an explicit `__init__` binds two fields to the SAME parameter. CPython returns
True; PROVED at cdac19a6, now REFUSED by the constructor scan.
"""
# pycsl-expected: FAIL
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
class C:
    def __init__(self, p: Dict[int, int]) -> None:
        self.d: Dict[int, int] = p
        self.g: Dict[int, int] = p

    #@ ensures \result == False
    #@ assigns self.d
    def m(self) -> bool:
        if 1 in self.g:
            return False
        self.d[1] = 5
        return 1 in self.g


if __name__ == "__main__":
    assert C({}).m() is True
