r"""and returns operand not bool"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a = 0
    b = 5
    return (a and b) + 1


if __name__ == "__main__":
    print("CPython:", probe())
