r"""try in loop with continue on missing key"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    n = 0
    for k in ["a", "b", "c"]:
        try:
            v = d[k]
        except KeyError:
            continue
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
