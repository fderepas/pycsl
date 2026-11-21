r"""append inside comprehension"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    ys: List[int] = []
    zs = [ys.append(x) for x in [1, 2]]
    return len(ys)


if __name__ == "__main__":
    print("CPython:", probe())
