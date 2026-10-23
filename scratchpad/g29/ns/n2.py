r"""None returned from function compared"""
from typing import List, Dict, Optional
_ = 0  # anchor


def f(flag: bool) -> Optional[int]:
    if flag:
        return 1
    return None


#@ ensures \result == True
def probe() -> bool:
    return f(False) == 0


if __name__ == "__main__":
    print("CPython:", probe())
