r"""M8 — a per-field `field(kw_only=True)` REORDERS the positional list: `yfld` becomes
the FIRST positional parameter, so `Pee(5, xfld=1).yfld` is 5."""
from dataclasses import dataclass, field

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = field(kw_only=True, default=0)
    yfld: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee(5, xfld=1)
    return p.yfld
