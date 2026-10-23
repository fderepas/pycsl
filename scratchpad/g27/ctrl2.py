r"""CTRL2 — positive control for draft-1's two new module-scope arms: an ordinary module-scope
`getattr` on a fresh instance, and an ordinary mutating call on a module dict literal and a
module class instance, must all still VERIFY."""
_ = 0  # anchor
from typing import Dict


class C:
    def __init__(self) -> None:
        self.n = 0


D: Dict[str, int] = {"a": 1}
D.update({"b": 2})
D.pop("a")
c = C()
z = getattr(c, "n")


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return 7
