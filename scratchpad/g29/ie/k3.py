r"""del missing key caught"""
from typing import Dict, List, Set
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        del d["b"]
    except KeyError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
