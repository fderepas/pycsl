r"""float to int large"""
import math
_ = 0  # anchor


#@ ensures \result == 10000000000000000000000
def probe() -> int:
    return int(1e22)


if __name__ == "__main__":
    print("CPython:", probe())
