r"""G29 NT1 — NamedTuple default "a non-int default falls back to 0 (sound — never read before write)": a NEGATIVE literal default, omitted."""
from typing import NamedTuple
_ = 0  # anchor


class P(NamedTuple):
    x: int
    y: int = -5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    return p.y


if __name__ == "__main__":
    print("CPython:", probe())
