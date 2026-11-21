r"""Test 1631 - ROUTE #179 (gen #29): `try: c = C(-1) except ValueError: return 9; return 0` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(-1)
    except ValueError:
        return 9
    return 0
