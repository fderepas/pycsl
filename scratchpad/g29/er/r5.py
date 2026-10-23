r"""G29 ER5 — route #152 control: a `return` inside a NESTED def in `__init__` is not the constructor's."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.x = k


#@ ensures \result == 4
#@ assigns \nothing
def probe() -> int:
    c = C(4)
    return c.x
