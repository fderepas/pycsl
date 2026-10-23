r"""abs of min float and nan compare"""
import math
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    x = float("nan")
    return x == x


if __name__ == "__main__":
    print("CPython:", probe())
