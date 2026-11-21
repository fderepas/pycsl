r"""float floor division negative"""
import math
_ = 0  # anchor


#@ ensures \result == -3.0
def probe() -> float:
    return -7 // 2.0 + 1.0


if __name__ == "__main__":
    print("CPython:", probe())
