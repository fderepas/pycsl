r"""iterator next raising caught"""
from typing import List, Dict
_ = 0  # anchor


class It:
    def __init__(self) -> None:
        self.k = 0

    def __iter__(self) -> "It":
        return self

    def __next__(self) -> int:
        raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        for x in It():
            pass
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
