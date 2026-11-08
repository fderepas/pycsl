r"""math.floor of negative"""
import math
_ = 0  # anchor


#@ ensures \result == -2
def probe() -> int:
    return math.floor(-2.5)


if __name__ == "__main__":
    print("CPython:", probe())
