r"""N2 — the same for a COMPUTED name-free default `2 + 3` (a BinOp)."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = 2 + 3


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
