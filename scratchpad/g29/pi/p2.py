r"""G29 P2 — the same, read DIRECTLY."""
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    x: int

    def __post_init__(self) -> None:
        self.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
