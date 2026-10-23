r"""str.find returns -1, int parse of empty"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s = ""
    try:
        v = int(s)
    except ValueError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
