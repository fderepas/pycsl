r"""callee tuple unpack under no_exception"""
from typing import List, Dict, Tuple
_ = 0  # anchor


def two(s: str) -> int:
    a, b = s.split(",")
    return 0


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    return two("a")


if __name__ == "__main__":
    print("CPython:", probe())
