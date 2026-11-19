r"""Test 5079 -- gen #37 route #376 (expected FAIL): NEW shape: a `@property k` returning -1; `getattr(r, "k", 0) >= 0` PROVED at base (CPython -1). REFUSED now.
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x = 1

    @property
    def k(self) -> int:
        return -1

#@ ensures \result >= 0
def f(r: R) -> int:
    return getattr(r, "k", 0)

if __name__ == "__main__":
    assert f(R()) >= 0, f(R())
