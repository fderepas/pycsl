r"""NoReturn infinite loop that breaks"""
from typing import List, NoReturn
_ = 0  # anchor


def die() -> NoReturn:
    while True:
        break


#@ ensures \result == 1
def probe() -> int:
    die()
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
