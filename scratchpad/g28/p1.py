r"""P1 — carrier-rerun on the route-#145 arm: `field(default_factory=...)` carries NO
`default=` keyword, so the unwrap yields None and the field keeps the DEFINITE literal 0
for a SCALAR field."""
from dataclasses import dataclass, field

_ = 0  # anchor


def five() -> int:
    return 5


@dataclass
class Pee:
    xfld: int = field(default_factory=five)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
