r"""str() of negative"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    return len(str(-5))


if __name__ == "__main__":
    print("CPython:", probe())
