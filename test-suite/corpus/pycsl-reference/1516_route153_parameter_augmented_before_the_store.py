r"""Test 1516 - ROUTE #153 (gen #29): the same with `k += 1`; `C(5).x == 5` PROVED; CPython 6.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        k += 1
        self.x = k


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x

