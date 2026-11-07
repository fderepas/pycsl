r"""bool is an int subclass"""
from typing import List, Optional, Union
_ = 0  # anchor


def f(x: Union[int, str]) -> int:
    if isinstance(x, int):
        return 1
    return 2


#@ ensures \result == 2
def probe() -> int:
    return f(True)


if __name__ == "__main__":
    print("CPython:", probe())
