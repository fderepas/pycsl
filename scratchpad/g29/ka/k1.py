r"""keyword-only default"""
from typing import List, Dict
_ = 0  # anchor


def f(a: int, *, b: int = 3) -> int:
    return a + b


#@ ensures \result == 1
def probe() -> int:
    return f(1)


if __name__ == "__main__":
    print("CPython:", probe())
