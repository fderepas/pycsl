r"""M10 — the `KW_ONLY` sentinel: every field DECLARED AFTER `_: KW_ONLY` is
keyword-only, so `yfld` is not positional and `Pee(5)` is a TypeError; the model binds
the sentinel member itself as parameter 0."""
from dataclasses import dataclass, KW_ONLY

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = 0
    _: KW_ONLY = None
    yfld: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = Pee(1, yfld=7)
    return p.xfld
