r"""chained comparison short circuit with call"""
from typing import List, Dict
_ = 0  # anchor


calls: List[int] = [0]


def side() -> int:
    calls[0] = calls[0] + 1
    return 5


#@ ensures \result == 2
def probe() -> int:
    b = 1 < 0 < side()
    return calls[0] + 2


if __name__ == "__main__":
    print("CPython:", probe())
