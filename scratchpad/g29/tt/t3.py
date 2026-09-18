r"""zero float truthiness"""
from typing import List, Dict, Set
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    f = 0.0
    if f:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
