r"""dict copy independence"""
import copy
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    a: Dict[str, int] = {"k": 0}
    b = dict(a)
    b["k"] = 5
    return a["k"]


if __name__ == "__main__":
    print("CPython:", probe())
