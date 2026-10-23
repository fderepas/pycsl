r"""Test 1495 - ROUTE #150 (gen #29): `__init__` stores `self.x = 1` then calls `self._setup()`, which stores 7; `{ x = 1 }` and `P().x == 1` PROVED; CPython 7. A call on `self` inside a constructor is an opaque effect.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 1
        self._setup()

    #@ assigns self.x
    def _setup(self) -> None:
        self.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x

