r"""argument unpacking from list"""
from typing import List, Dict
_ = 0  # anchor


def f(a: int, b: int) -> int:
    return a - b


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2]
    return f(*xs)


if __name__ == "__main__":
    print("CPython:", probe())
