"""Test 0206 — Python Reference 8.8.1: Multiple inheritance"""
_ = 0  # anchor
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


#@ ensures \result == 1
def test_multiple_inheritance() -> int:
    """Ref 8.8.1: `C(A, B)` resolves `who` to A's by the MRO, so the result is 1 and NOT 2.

    This driver replaces an EMPTY PLACEHOLDER (`return 0` under `ensures \result == 0`,
    which the tail return alone discharged). The MRO is modelled FAITHFULLY and
    DISCRIMINATINGLY — measured as a full 2x2: with the bases reversed to `C(B, A)` the
    true answer 2 proves and the false answer 1 fails closed, and in this order the true
    answer 1 proves and the false answer 2 fails closed. So the contract below is a real
    claim about method resolution, not a claim the `return` discharges by itself.
    """
    c = C()
    return c.who()


if __name__ == "__main__":
    assert test_multiple_inheritance() == 1
