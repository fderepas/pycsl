r"""datatype construction"""
from typing import List
_ = 0  # anchor


#@ datatype Shape = Circle(r: int) | Square(s: int)


#@ ensures \result == 0
def probe() -> int:
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
