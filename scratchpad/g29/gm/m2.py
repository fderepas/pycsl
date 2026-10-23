r"""G29 GM2 — a module-level DICT mutated through a method call in a function declaring `assigns \nothing`."""
from typing import Dict
_ = 0  # anchor
D: Dict[int, int] = {1: 1}


#@ assigns \nothing
def a() -> None:
    D[1] = 9


#@ ensures \result == 1
def b() -> int:
    a()
    return D[1]


if __name__ == "__main__":
    print("CPython:", b())
