r"""str.index missing caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s = "abc"
    try:
        v = s.index("z")
    except ValueError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
