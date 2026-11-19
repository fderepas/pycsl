r"""Test 4615 -- gen #37 route #343 (expected FAIL): witness h06: `(s := self) - s` with a user `__sub__` returning 1; `ensures \result == 0` PROVED (CPython 1). REFUSED (erased value into `-> int`).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        return (s := self) - s

if __name__ == "__main__":
    assert W().m() == 1
