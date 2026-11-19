r"""NoReturn conditional raise"""
from typing import List, NoReturn
_ = 0  # anchor


def die(x: int) -> NoReturn:
    if x > 0:
        raise ValueError()


#@ ensures \result == 1
def probe() -> int:
    die(0)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
