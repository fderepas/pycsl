r"""G29 GM3 — a module-level list APPENDED in a function declaring `assigns \nothing`."""
from typing import List
_ = 0  # anchor
G: List[int] = []


#@ assigns \nothing
def a() -> None:
    G.append(9)


#@ ensures \result == 0
def b() -> int:
    a()
    return len(G)


if __name__ == "__main__":
    print("CPython:", b())
