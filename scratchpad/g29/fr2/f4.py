r"""G29 FR2-4 — no assigns clause at all; module function mutates a list argument."""
from typing import List
_ = 0  # anchor


def poke(xs: List[int]) -> None:
    xs[0] = 5


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0]
    b = xs[0]
    poke(xs)
    return xs[0] - b


if __name__ == "__main__":
    print("CPython:", probe())
