r"""pure function with side effect used in contract"""
from typing import List
_ = 0  # anchor


counter: List[int] = [0]


#@ pure
def bump() -> int:
    counter[0] = counter[0] + 1
    return counter[0]


#@ ensures \result == bump()
def probe() -> int:
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
