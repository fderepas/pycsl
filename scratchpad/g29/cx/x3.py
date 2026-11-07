r"""module constant tuple element"""
from typing import List, Dict, Optional
_ = 0  # anchor


T = (1, 2)


#@ ensures \result == 2
def probe() -> int:
    return T[0]


if __name__ == "__main__":
    print("CPython:", probe())
