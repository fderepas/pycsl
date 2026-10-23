r"""closure captures a mutable local"""
from typing import List, Dict, Callable
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    n = 1

    def read() -> int:
        return n

    n = 5
    return read()


if __name__ == "__main__":
    print("CPython:", probe())
