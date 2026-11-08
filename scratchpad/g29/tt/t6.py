r"""dict truthiness after store"""
from typing import List, Dict, Set
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {}
    d["a"] = 1
    if d:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
