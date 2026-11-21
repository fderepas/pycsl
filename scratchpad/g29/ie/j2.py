r"""missing int key read, no try"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {1: 1}
    return d[2]

if __name__ == "__main__":
    print("CPython:", probe())
