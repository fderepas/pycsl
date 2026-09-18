r"""module constant used after del and rebind"""
from typing import List, Dict
_ = 0  # anchor


N = 3
del N
N = 5


#@ ensures \result == 3
def probe() -> int:
    return N


if __name__ == "__main__":
    print("CPython:", probe())
