r"""Test 1498 - ROUTE #150 (gen #29): `init_p(self)` inside `__init__`, the function storing `p.x = 7`; `P().x == 1` PROVED; CPython 7.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 1
        init_p(self)


#@ assigns p.x
def init_p(p: P) -> None:
    p.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x

