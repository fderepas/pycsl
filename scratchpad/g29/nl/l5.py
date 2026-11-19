r"""None returned then compared in same function"""
from typing import List, Dict, Optional
_ = 0  # anchor


def g() -> Optional[int]:
    return None


#@ ensures \result == True
def probe() -> bool:
    v = g()
    return v == 0


if __name__ == "__main__":
    print("CPython:", probe())
