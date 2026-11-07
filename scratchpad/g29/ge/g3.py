r"""raise in nested function called"""
from typing import List, Iterator
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    def inner() -> int:
        raise ValueError()

    try:
        inner()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
