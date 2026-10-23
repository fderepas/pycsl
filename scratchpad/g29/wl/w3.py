r"""walrus short-circuit not evaluated"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    y = 1
    if False and (y := 5) > 0:
        pass
    return y


if __name__ == "__main__":
    print("CPython:", probe())
