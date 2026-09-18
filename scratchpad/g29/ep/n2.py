r"""no_exception all with an unchecked op"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception \all
#@ ensures \result == 0
def probe() -> int:
    s = "ab"
    return len(s) * 0


if __name__ == "__main__":
    print("CPython:", probe())
