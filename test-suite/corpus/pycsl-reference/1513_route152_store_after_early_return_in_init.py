r"""Test 1513 - ROUTE #152 (gen #29): `class C: x = 0` with `__init__: if k < 0: return; self.x = k`; the top-level store after the conditional return was made definite (`{ x = (- 1) }`) and `C(-1).x == -1` PROVED; CPython 0. A `return` in a constructor makes the construction opaque.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    x = 0

    def __init__(self, k: int) -> None:
        if k < 0:
            return
        self.x = k


#@ ensures \result == -1
#@ assigns \nothing
def probe() -> int:
    c = C(-1)
    return c.x

