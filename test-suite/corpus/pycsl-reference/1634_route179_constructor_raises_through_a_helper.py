r"""Test 1634 - ROUTE #179 carrier (gen #29): `__init__` raises only through a module helper `check(v)`; `C(-1)` under `except ValueError: return 9` PROVED `\result == 0` on the #179 draft (CPython 9). Constructor raises are now closed over same-file calls.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def check(v: int) -> None:
    if v < 0:
        raise ValueError()


class C:
    def __init__(self, v: int) -> None:
        check(v)
        self.v = v


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(-1)
    except ValueError:
        return 9
    return 0
