r"""contract reads a list length after append"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \length(xs) == 1
def f(xs: List[int]) -> None:
    xs.append(1)


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2]
    f(xs)
    return len(xs) - 3


if __name__ == "__main__":
    print("CPython:", probe())
