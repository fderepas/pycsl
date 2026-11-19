r"""D1b — the same deferral, second carrier: a name-free BinOp RHS."""
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
