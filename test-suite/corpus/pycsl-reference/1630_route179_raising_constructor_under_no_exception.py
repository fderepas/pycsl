r"""Test 1630 - ROUTE #179 (gen #29): `C(-1)` where `__init__` raises ValueError on a negative argument PROVED `#@ no_exception ValueError` (CPython ValueError): the construction is lowered to a record literal and the raise is gone. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    c = C(-1)
    return 0
