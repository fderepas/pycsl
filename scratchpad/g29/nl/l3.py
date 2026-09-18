r"""None param default read"""
from typing import List, Dict, Optional
_ = 0  # anchor


def f(x: Optional[int] = None) -> int:
    return 1 if x == 0 else 0


#@ ensures \result == 1
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
