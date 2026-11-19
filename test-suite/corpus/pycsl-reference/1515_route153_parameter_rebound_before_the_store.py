r"""Test 1515 - ROUTE #153 (gen #29): `__init__: k = k + 1; self.x = k` — the capture substituted the ARGUMENT for `k`, built `{ x = 5 }` for `C(5)` and `C(5).x == 5` PROVED; CPython 6. A parameter the constructor rebinds leaves the capture set.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        k = k + 1
        self.x = k


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x

