r"""Test 1579 - ROUTE #169 (gen #29): an inlined method unpacks `a, b = d, d`; only single-name targets were freshened, so it overwrote the caller's `a` and `a = 7; _g.f(100); return a` PROVED `\result == 100` (CPython 7). Tuple-unpack targets are now freshened.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, d: int) -> int:
        a, b = d, d
        return a + b


_g = C(0)


#@ ensures \result == 100
def probe() -> int:
    a = 7
    _g.f(100)
    return a
