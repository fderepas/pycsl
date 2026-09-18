r"""dataclass post_init raising caught"""
from typing import List
_ = 0  # anchor


from dataclasses import dataclass


@dataclass
class P:
    v: int

    def __post_init__(self) -> None:
        if self.v < 0:
            raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        p = P(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
