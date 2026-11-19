r"""while with else-less break count"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [1, 2, 3, 4]
    c = 0
    for x in xs:
        if x == 3:
            break
        c = c + 1
    return c


if __name__ == "__main__":
    print("CPython:", probe())
