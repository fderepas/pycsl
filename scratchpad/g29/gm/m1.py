r"""G29 GM1 — a module-level LIST mutated by a function declaring `assigns \nothing`."""
from typing import List
_ = 0  # anchor
G: List[int] = [1, 2]


#@ assigns \nothing
def a() -> None:
    G[0] = 9


#@ ensures \result == 1
def b() -> int:
    a()
    return G[0]


if __name__ == "__main__":
    print("CPython:", b())
