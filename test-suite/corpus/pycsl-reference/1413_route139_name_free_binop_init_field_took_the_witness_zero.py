r"""Test 1413 — ROUTE #139, second carrier: `self.start = 2 + 3` is a name-free `BinOp`, equally unmatched by `field_defaults` and equally exempt from route #79 unknown-marking. `\result == 0` PROVED while CPython returns 5. A name-free COMPUTED right-hand side is now marked UNKNOWN.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    start: int

    def __init__(self) -> None:
        self.start = 2 + 3


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.start