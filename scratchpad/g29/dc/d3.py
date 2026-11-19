r"""G29 DC3 — NamedTuple `_replace`."""
from typing import NamedTuple
_ = 0  # anchor


class P(NamedTuple):
    x: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    q = p._replace(x=5)
    return q.x


if __name__ == "__main__":
    print("CPython:", probe())
