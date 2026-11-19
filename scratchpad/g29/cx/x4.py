r"""module constant string indexed"""
from typing import List, Dict, Optional
_ = 0  # anchor


S = "abc"


#@ ensures \result == 1
def probe() -> int:
    return len(S[0])


if __name__ == "__main__":
    print("CPython:", probe())
