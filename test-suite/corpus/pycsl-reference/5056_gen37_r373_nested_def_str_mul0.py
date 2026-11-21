r"""Test 5056 -- gen #37 route #373 (expected FAIL): a nested `-> str` def: `t * 0 == 0` PROVED at base (CPython `"" == 0` is False). FAILS now (the call result is erased).
"""
# pycsl-expected: FAIL
class P:
    #@ ensures \result == 1
    def m(self) -> int:
        def g() -> str:
            return "a"
        t = g()
        return 1 if t * 0 == 0 else 0

if __name__ == "__main__":
    assert P().m() == 1, P().m()
