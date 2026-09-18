r"""string multiplication length"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s = "ab" * -1
    return len(s) + 1


if __name__ == "__main__":
    print("CPython:", probe())
