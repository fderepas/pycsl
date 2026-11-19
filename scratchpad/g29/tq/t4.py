r"""chained assignment aliasing lists"""
from typing import List, Tuple, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    a = b = [0]
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    print("CPython:", probe())
