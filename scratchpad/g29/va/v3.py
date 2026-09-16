r"""G29 VA3 — NamedTuple with an omitted INT default."""
from typing import NamedTuple
_ = 0  # anchor


class P(NamedTuple):
    x: int
    y: int = 5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    return p.y


if __name__ == "__main__":
    print("CPython:", probe())
