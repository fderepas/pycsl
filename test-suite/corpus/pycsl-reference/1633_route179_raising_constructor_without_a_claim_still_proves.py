r"""Test 1633 - ROUTE #179 control (gen #29): constructing a class whose `__init__` may raise, in a function that neither claims `no_exception` nor catches the exception, is unaffected: `C(3).v == 3` proves.
"""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


#@ ensures \result == 3
def probe() -> int:
    c = C(3)
    return c.v
