r"""math.ceil"""
import math
_ = 0  # anchor


#@ ensures \result == -2
def probe() -> int:
    return math.ceil(-2.5) - 0


if __name__ == "__main__":
    print("CPython:", probe())
