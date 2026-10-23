r"""Test 1496 - ROUTE #150 (gen #29): `me = self; me.x = 7` inside `__init__`; `P().x == 1` PROVED; CPython 7. Any load of bare `self` in a constructor is an opaque effect.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 1
        me = self
        me.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x

