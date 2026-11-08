r"""dict store via setdefault inside comprehension"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {}
    zs = [d.setdefault(x, x) for x in [1, 2]]
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
