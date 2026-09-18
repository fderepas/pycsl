r"""int comparison chain with mixed types"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    return 1 == 1.0


if __name__ == "__main__":
    print("CPython:", probe())
