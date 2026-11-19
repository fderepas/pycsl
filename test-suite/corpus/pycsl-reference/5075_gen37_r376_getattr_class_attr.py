r"""Test 5075 -- gen #37 route #376 (expected FAIL): `getattr(r, "k", 0)` where `k = -1` is a CLASS attribute of the record R (fields: x); folded to the default 0, `\result >= 0` PROVED (CPython -1). REFUSED now (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
class R:
    k = -1
    def __init__(self) -> None:
        self.x = 1

#@ ensures \result >= 0
def f(r: R) -> int:
    return getattr(r, "k", 0)

if __name__ == "__main__":
    assert f(R()) >= 0, f(R())
