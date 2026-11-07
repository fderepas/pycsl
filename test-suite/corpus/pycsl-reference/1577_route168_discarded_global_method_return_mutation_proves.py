r"""Test 1577 - ROUTE #168 control (gen #29): with the discarded return value evaluated, `_g.run()` in statement position increments `_g.x` and `_g.x - a == 1` PROVES (FAILS at HEAD).
"""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ assigns self.x
    def bumpret(self) -> int:
        self.x = self.x + 1
        return self.x

    #@ assigns self.x
    def run(self) -> int:
        return self.bumpret()


_g = C(0)


#@ ensures \result == 1
def probe() -> int:
    a = _g.x
    _g.run()
    return _g.x - a


