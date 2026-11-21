r"""G29 DC1 — `field(init=False, default=5)` is NOT a constructor parameter; a later field is."""
from dataclasses import dataclass, field
_ = 0  # anchor


@dataclass
class P:
    y: int = field(init=False, default=5)
    x: int = 0


#@ ensures \result == 3
#@ assigns \nothing
def probe() -> int:
    p = P(3)
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
