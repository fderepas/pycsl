r"""augmented string concat"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    s = "a"
    s += "bc"
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
