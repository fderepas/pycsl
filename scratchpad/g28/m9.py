r"""M9 — `field(default=5)` is the dataclass spelling of a default value; the RHS is a
CALL, not a Constant, so `field_defaults` does not match it."""
from dataclasses import dataclass, field

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = field(default=5)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
