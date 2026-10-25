r"""Test 5054 -- gen #37 route #373 (expected FAIL): `t * t >= 0` with `__mul__` -> -1; PROVED at base (CPython -1). REFUSED now.
"""
# pycsl-expected: FAIL
class W:
    def __mul__(self, o: object) -> int:
        return -1

    #@ ensures \result >= 0
    def m(self) -> int:
        def g() -> "W":
            return self
        t = g()
        return t * t

if __name__ == "__main__":
    assert W().m() >= 0, W().m()
