r"""G29 DC4 — the `field(init=False, default=5)` field itself after `P(3)`."""
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
    return p.y


if __name__ == "__main__":
    print("CPython:", probe())
