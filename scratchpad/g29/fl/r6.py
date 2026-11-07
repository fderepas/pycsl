r"""float equality 0.1+0.2"""
import math
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    return 0.1 + 0.2 == 0.3


if __name__ == "__main__":
    print("CPython:", probe())
