r"""None default optional param"""
from typing import List, Optional, Union
_ = 0  # anchor


def f(x: Optional[int] = None) -> int:
    if x is None:
        return 0
    return x


#@ ensures \result == 0
def probe() -> int:
    return f(0) + f(5)


if __name__ == "__main__":
    print("CPython:", probe())
