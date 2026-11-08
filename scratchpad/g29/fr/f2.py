r"""G29 FR2 — `random.shuffle`-like opaque library mutation: `xs.reverse()` on a parameter."""
from typing import List
_ = 0  # anchor


#@ requires len(xs) == 2
#@ assigns \nothing
def f(xs: List[int]) -> None:
    xs.reverse()


#@ requires len(xs) == 2 and xs[0] == 5 and xs[1] == 1
#@ ensures \result == 5
def probe(xs: List[int]) -> int:
    f(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe([5, 1]))
