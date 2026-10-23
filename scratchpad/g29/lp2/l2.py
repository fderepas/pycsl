r"""for loop over range with loop var reassigned"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 10
def probe() -> int:
    s = 0
    for i in range(5):
        i = 10
        s = s + 1
    return s


if __name__ == "__main__":
    print("CPython:", probe())
