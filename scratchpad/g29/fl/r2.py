r"""int truncation of negative float"""
import math
_ = 0  # anchor


#@ ensures \result == -3
def probe() -> int:
    return int(-2.7)


if __name__ == "__main__":
    print("CPython:", probe())
