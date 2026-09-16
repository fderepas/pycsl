r"""CTRL2b — positive control for draft-2's module-scope arms, WITHOUT a folded const dict
(the first attempt tripped #132's own alias/mutation rule, so it measured nothing)."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0


c = C()
z = getattr(c, "n")


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return 7
