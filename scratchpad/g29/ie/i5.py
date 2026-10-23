r"""wrong handler type: ZeroDivisionError not caught by KeyError, outer catches"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    z = 0
    try:
        try:
            v = 10 // z
        except KeyError:
            return 1
    except ZeroDivisionError:
        return 9
    return v

if __name__ == "__main__":
    print("CPython:", probe())
