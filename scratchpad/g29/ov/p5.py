r"""or returns first truthy"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    a = 0
    b = 7
    return a or b


if __name__ == "__main__":
    print("CPython:", probe())
