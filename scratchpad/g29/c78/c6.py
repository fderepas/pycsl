r"""callee float() caught"""
from typing import List, Dict, Tuple
_ = 0  # anchor


def conv(s: str) -> float:
    return float(s)


#@ ensures \result == 0
def probe() -> int:
    try:
        f = conv("x")
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
