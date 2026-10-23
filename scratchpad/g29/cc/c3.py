r"""float key equal to int key"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    d: Dict[float, int] = {1.0: 1}
    d[1] = 2
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
