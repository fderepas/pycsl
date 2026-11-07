r"""true division of ints"""
import math
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> float:
    return 7 / 2


if __name__ == "__main__":
    print("CPython:", probe())
