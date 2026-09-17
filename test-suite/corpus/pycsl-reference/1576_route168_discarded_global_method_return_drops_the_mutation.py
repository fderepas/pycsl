r"""Test 1576 - ROUTE #168 (gen #29): `_g.run()` in statement position, with `run` returning `self.bumpret()` (a mutator), PROVED `_g.x - a == 0` - the mutation was dropped with the discarded return value (CPython 1).
"""
# pycsl-expected: FAIL
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


#@ ensures \result == 0
def probe() -> int:
    a = _g.x
    _g.run()
    return _g.x - a


