r"""Test 5053 -- gen #37 route #373 (expected FAIL): `t != t` on the nested call result, user `__ne__` -> True; PROVED `\result == 0` at base (CPython 1). FAILS now (uninterpreted `pycsl_py_ne`).
"""
# pycsl-expected: FAIL
class W:
    def __ne__(self, o: object) -> bool:
        return True

    #@ ensures \result == 0
    def m(self) -> int:
        def g() -> "W":
            return self
        t = g()
        return 1 if t != t else 0

if __name__ == "__main__":
    assert W().m() == 0, W().m()
