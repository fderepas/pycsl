r"""G1 — carrier of MY OWN #139 repair: `_lit79` exempts every `ast.Tuple`, but
`field_defaults` captures no tuple, so a tuple field still falls to the witness."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.t = (1, 2)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.t[0]
