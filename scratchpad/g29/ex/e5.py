r"""nested function catches, outer sees normal return"""
from typing import List, Dict
_ = 0  # anchor


def inner() -> int:
    try:
        raise ValueError()
    except ValueError:
        return 3


#@ ensures \result == 0
def probe() -> int:
    return inner()


if __name__ == "__main__":
    print("CPython:", probe())
