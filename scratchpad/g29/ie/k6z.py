r"""no_exception ZeroDivisionError in caller; helper reads a missing key"""
from typing import Dict
_ = 0  # anchor


def get(d: Dict[str, int]) -> int:
    return 10 // (len(d) - 1)


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    v = get(d)
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
