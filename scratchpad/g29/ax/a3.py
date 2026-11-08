r"""assigns nothing but writes a global list"""
from typing import List
_ = 0  # anchor


G: List[int] = [0]


#@ assigns \nothing
def f() -> None:
    G[0] = 9


#@ ensures \result == 0
def probe() -> int:
    f()
    return G[0]


if __name__ == "__main__":
    print("CPython:", probe())
