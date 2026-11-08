r"""RecursionError caught"""
from typing import List, Dict, Optional
_ = 0  # anchor


def deep(n: int) -> int:
    return deep(n + 1)


#@ ensures \result == 0
def probe() -> int:
    try:
        deep(0)
    except RecursionError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
