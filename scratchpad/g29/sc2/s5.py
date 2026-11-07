r"""global shadowed by local assigned later is UnboundLocal"""
from typing import List
_ = 0  # anchor


G = 5


#@ ensures \result == 5
def probe() -> int:
    y = G
    G = 3
    return y


if __name__ == "__main__":
    print("CPython:", probe())
