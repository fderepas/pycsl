r"""Test 5321 -- gen #37 route #386 (expected PASS): control: a METHOD named `max` called as `self.max()` (class scope, not a shadow); PROVED.
"""
# pycsl-expected: PASS
class W:
    def __init__(self) -> None:
        self.a: int = 3

    #@ ensures \result == 7
    #@ assigns \nothing
    def max(self) -> int:
        return 7

    #@ ensures \result == 7
    #@ assigns \nothing
    def m(self) -> int:
        return self.max()


if __name__ == "__main__":
    assert W().m() == 7
