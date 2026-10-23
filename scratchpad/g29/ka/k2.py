r"""positional default overridden by keyword"""
from typing import List, Dict
_ = 0  # anchor


def f(a: int, b: int = 3) -> int:
    return a - b


#@ ensures \result == -2
def probe() -> int:
    return f(b=10, a=1)


if __name__ == "__main__":
    print("CPython:", probe())
