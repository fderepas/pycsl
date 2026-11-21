r"""module-qualified constant shadowed locally"""
from typing import List
_ = 0  # anchor


import libc

LIMIT = 9


#@ ensures \result == 9
def probe() -> int:
    return libc.LIMIT


if __name__ == "__main__":
    print("CPython:", probe())
