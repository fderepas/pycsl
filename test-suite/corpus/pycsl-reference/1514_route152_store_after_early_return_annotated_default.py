r"""Test 1514 - ROUTE #152 (gen #29): the same with an annotated class-level default `x: int = 0`; `C(-1).x == -1` PROVED; CPython 0.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    x: int = 0

    def __init__(self, k: int) -> None:
        if k < 0:
            return
        self.x = k


#@ ensures \result == -1
#@ assigns \nothing
def probe() -> int:
    c = C(-1)
    return c.x

