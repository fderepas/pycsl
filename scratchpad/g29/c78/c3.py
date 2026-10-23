r"""callee's callee missing key"""
from typing import List, Dict, Tuple
_ = 0  # anchor


def get(d: Dict[str, int]) -> int:
    return d["b"]


def mid(d: Dict[str, int]) -> int:
    return get(d)


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    return mid(d) * 0


if __name__ == "__main__":
    print("CPython:", probe())
