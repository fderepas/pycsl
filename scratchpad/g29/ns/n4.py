r"""None default param compared"""
from typing import List, Dict, Optional
_ = 0  # anchor


def f(x: Optional[int] = None) -> bool:
    return x == 0


#@ ensures \result == True
def probe() -> bool:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
