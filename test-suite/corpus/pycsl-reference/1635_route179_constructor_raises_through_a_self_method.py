r"""Test 1635 - ROUTE #179 carrier (gen #29): `__init__` raises only through `self.check()`; `C(-1)` under `except ValueError: return 9` PROVED `\result == 0` on the #179 draft (CPython 9).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
        self.check()

    def check(self) -> None:
        if self.v < 0:
            raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(-1)
    except ValueError:
        return 9
    return 0
