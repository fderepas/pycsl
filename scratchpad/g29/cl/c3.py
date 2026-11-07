r"""nested function mutating enclosing via nonlocal then read"""
from typing import List, Dict, Callable
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    n = 0

    def bump() -> None:
        nonlocal n
        n = n + 1

    bump()
    bump()
    return n


if __name__ == "__main__":
    print("CPython:", probe())
