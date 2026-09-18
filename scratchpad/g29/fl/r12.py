r"""float inf compare"""
import math
_ = 0  # anchor


#@ ensures \result == False
def probe() -> bool:
    return float("inf") > 1e308


if __name__ == "__main__":
    print("CPython:", probe())
