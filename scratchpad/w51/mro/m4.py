# pycsl-flags: --memory-model hoare
"""Probe: does PyCSL model MULTIPLE inheritance well enough for a NON-VACUOUS driver?
Python Reference 8.8.1. `C(A, B)` resolves `who()` to A's by MRO, so `\result == 1`."""
from dataclasses import dataclass


@dataclass
class A:
    v: int = 0

    #@ requires True
    #@ ensures \result == 1
    def who(self) -> int:
        return 1


@dataclass
class B:
    v: int = 0

    #@ requires True
    #@ ensures \result == 2
    def who(self) -> int:
        return 2


@dataclass
class C(A, B):
    v: int = 0


#@ requires True
#@ ensures \result == 2
def test_mro() -> int:
    c = C()
    return c.who()


if __name__ == "__main__":
    assert test_mro() == 1
