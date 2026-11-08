r"""Test 2309 — gen #36 r243 (expected FAIL): route #243: an explicit `__init__` doing `self.g = self.d` (Module 5 havocs `g`, losing the
alias). CPython returns True; PROVED at cdac19a6, now REFUSED by the constructor scan.
"""
# pycsl-expected: FAIL
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
class C:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {}
        self.g: Dict[int, int] = self.d

    #@ ensures \result == False
    #@ assigns self.d
    def m(self) -> bool:
        if 1 in self.g:
            return False
        self.d[1] = 5
        return 1 in self.g


if __name__ == "__main__":
    assert C().m() is True
