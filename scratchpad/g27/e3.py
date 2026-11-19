r"""E3 — carrier of MY #139 repair: a name-free BinOp on a STR field."""
_ = 0  # anchor


class C:
    s: str

    def __init__(self) -> None:
        self.s = "a" + "b"


#@ ensures \result == ""
#@ assigns \nothing
def probe() -> str:
    c = C()
    return c.s
