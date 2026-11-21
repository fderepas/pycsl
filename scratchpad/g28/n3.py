r"""N3 — the NamedTuple class-body path carries the SAME `isinstance(ast.Constant)` rule."""
from typing import NamedTuple

_ = 0  # anchor


class Pee(NamedTuple):
    xfld: int = -7


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
