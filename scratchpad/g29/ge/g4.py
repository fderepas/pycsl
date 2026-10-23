r"""raise via function stored in list"""
from typing import List, Iterator
_ = 0  # anchor


def boom() -> int:
    raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    fs = [boom]
    try:
        fs[0]()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
