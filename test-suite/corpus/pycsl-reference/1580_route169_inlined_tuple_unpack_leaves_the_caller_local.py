r"""Test 1580 - ROUTE #169 control (gen #29): with the tuple-unpack targets freshened the caller's `a` survives the inlined call and `\result == 7` PROVES (FAILS at HEAD).
"""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, d: int) -> int:
        a, b = d, d
        return a + b


_g = C(0)


#@ ensures \result == 7
def probe() -> int:
    a = 7
    _g.f(100)
    return a
