r"""match sequence pattern length"""
from typing import List, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    match xs:
        case [a, b]:
            return 1
        case _:
            return 2


if __name__ == "__main__":
    print("CPython:", probe())
