r"""Test 5081 -- gen #37 route #376 (expected FAIL): NEW shape: `getattr(r, "__module__", 5)` is the module name for every instance; folded to 5, PROVED at base (CPython "__main__"). REFUSED now.
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x = 1

#@ ensures \result == 5
def f(r: R) -> int:
    return getattr(r, "__module__", 5)

if __name__ == "__main__":
    assert f(R()) == 5, f(R())
