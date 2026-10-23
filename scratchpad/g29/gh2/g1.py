r"""ghost variable used in a real expression"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    #@ ghost int g = 1
    x = 0
    #@ assert g == 1
    return x + 0


if __name__ == "__main__":
    print("CPython:", probe())
