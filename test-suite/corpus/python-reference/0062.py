"""Test 0062 — Python Reference 3.2.10.1: Special attributes"""
_ = 0  # anchor


class Point:
    def __init__(self) -> None:
        self.x: int = 3
        self.y: int = 4


#@ ensures \result == 7
#@ assigns \nothing
def test_special_attributes() -> int:
    """Ref 3.2.10.1: instance attributes are looked up on the object, and the contract
    SAYS what the two of them sum to. (`__dict__` itself has no model in PyCSL — see
    `docs/pycsl-ub-catalog`; the checkable part of the reference is the attribute
    ACCESS.) Previously the whole body was `return 0` (relaunch #46,
    `bin/check-vacuous-drivers.py`)."""
    p = Point()
    return p.x + p.y

if __name__ == "__main__":
    assert test_special_attributes() == 7
