r"""G29 NT2 — NamedTuple default that is a MODULE CONSTANT, omitted."""
from typing import NamedTuple
_ = 0  # anchor
K = 5


class P(NamedTuple):
    x: int
    y: int = K


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    return p.y


if __name__ == "__main__":
    print("CPython:", probe())
