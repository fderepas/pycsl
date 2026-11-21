r"""round half to even"""
import math
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return round(2.5)


if __name__ == "__main__":
    print("CPython:", probe())
