r"""getitem raising caught"""
from typing import List, Dict
_ = 0  # anchor


class S:
    def __init__(self) -> None:
        self.k = 0

    def __getitem__(self, i: int) -> int:
        raise KeyError()


#@ ensures \result == 0
def probe() -> int:
    s = S()
    try:
        v = s[0]
    except KeyError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
