r"""round with ndigits"""
import math
_ = 0  # anchor


#@ ensures \result == 2.68
def probe() -> float:
    return round(2.675, 2)


if __name__ == "__main__":
    print("CPython:", probe())
