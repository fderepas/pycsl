r"""dict iteration order and values sum"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"b": 2, "a": 1}
    for k in d:
        return d[k] - 2 + 0 * len(k)
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
