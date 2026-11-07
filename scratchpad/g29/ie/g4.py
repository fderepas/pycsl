r"""G29 IE-G4 — `assigns \nothing` holds only on the dead-handler path."""
from typing import List
_ = 0  # anchor


#@ requires len(xs) >= 1
#@ assigns \nothing
def f(xs: List[int]) -> None:
    ys: List[int] = []
    try:
        v = ys[0]
    except IndexError:
        xs[0] = 5


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0]
    a = xs[0]
    f(xs)
    return xs[0] - a


if __name__ == "__main__":
    print("CPython:", probe())
