r"""missing key read in called helper, handler in caller"""
from typing import Dict, List, Set
_ = 0  # anchor


def get(d: Dict[str, int]) -> int:
    return d["b"]


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = get(d)
    except KeyError:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
