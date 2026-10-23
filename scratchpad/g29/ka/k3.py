r"""varargs count"""
from typing import List, Dict
_ = 0  # anchor


def f(*xs: int) -> int:
    return len(xs)


#@ ensures \result == 0
def probe() -> int:
    return f(1, 2, 3)


if __name__ == "__main__":
    print("CPython:", probe())
