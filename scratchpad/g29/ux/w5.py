r"""len dunder raising caught"""
from typing import List, Dict
_ = 0  # anchor


class S:
    def __init__(self) -> None:
        self.k = 0

    def __len__(self) -> int:
        raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        n = len(S())
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
