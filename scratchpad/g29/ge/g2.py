r"""raise inside a lambda called"""
from typing import List, Iterator
_ = 0  # anchor


def boom() -> int:
    raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    f = lambda: boom()
    try:
        f()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
