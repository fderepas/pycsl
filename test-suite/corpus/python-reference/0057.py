"""Test 0057 — Python Reference 3.2.8.8: Classes"""
_ = 0  # anchor


class Counter:
    """A class object: `__init__` sets instance state, a method reads and writes it."""

    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump(self) -> None:
        self.n = self.n + 1


#@ ensures \result == 2
#@ assigns \nothing
def test_classes() -> int:
    """Ref 3.2.8.8: a class defines a type whose instances carry per-instance state, and
    the contract SAYS what two `bump()` calls do. Previously the whole body was
    `\"\"\"Ref 3.2.8.8: Classes.\"\"\"; return 0` (relaunch #46,
    `bin/check-vacuous-drivers.py`)."""
    c = Counter()
    c.bump()
    c.bump()
    return c.n

if __name__ == "__main__":
    assert test_classes() == 2
