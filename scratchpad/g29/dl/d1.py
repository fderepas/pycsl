r"""del local then rebind"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    x = 1
    del x
    x = 2
    return x


if __name__ == "__main__":
    print("CPython:", probe())
