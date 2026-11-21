r"""tuple return and unpack order"""
from typing import List, Tuple, Dict
_ = 0  # anchor


def f() -> Tuple[int, int]:
    return 1, 2


#@ ensures \result == 1
def probe() -> int:
    a, b = f()
    return b


if __name__ == "__main__":
    print("CPython:", probe())
