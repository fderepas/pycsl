r"""missing key read inside comprehension caught"""
from typing import Dict, List, Set
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        xs = [d[k] for k in ["a", "b"]]
    except KeyError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
