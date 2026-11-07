r"""Test 5055 -- gen #37 route #373 (expected FAIL): `t == t` with `__eq__` -> False on an unannotated nested call; PROVED `\result == 1` at base (CPython 0). FAILS now.
"""
# pycsl-expected: FAIL
class W:
    def __eq__(self, o: object) -> bool:
        return False

    #@ ensures \result == 1
    def m(self) -> int:
        def g():
            return self
        t = g()
        return 1 if t == t else 0

if __name__ == "__main__":
    assert W().m() == 1, W().m()
