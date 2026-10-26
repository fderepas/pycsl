r"""Test 5680 -- gen #37 CONTROL routes #393 (expected PASS): `E(Exception)` built with positional arguments only, and `F(ValueError)` with a plain `def __init__(self, code)` called `F(code=3)`; PROVED (CPython 3).
"""
# pycsl-expected: PASS
class E(Exception):
    pass
class F(ValueError):
    def __init__(self, code: int) -> None:
        super().__init__(code)
        self.code: int = code
#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    e = E("m", 1, 2)
    g = F(code=3)
    return 1
if __name__ == "__main__":
    assert f() == 1
