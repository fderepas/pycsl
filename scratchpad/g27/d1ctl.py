r"""D1-CTL — the same shape with a POSITIVE literal: `field_defaults` captures it, so the
true value proves and the false one must not."""
_ = 0  # anchor


class C:
    start: int

    def __init__(self) -> None:
        self.start = 7


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.start
