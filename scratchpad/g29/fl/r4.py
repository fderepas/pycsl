r"""float modulo negative"""
import math
_ = 0  # anchor


#@ ensures \result == -1.0
def probe() -> float:
    return -7 % 2.0


if __name__ == "__main__":
    print("CPython:", probe())
