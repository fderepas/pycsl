r"""imported class constant"""
from typing import List
_ = 0  # anchor


from libc import Cfg


#@ ensures \result == 0
def probe() -> int:
    return Cfg.SIZE


if __name__ == "__main__":
    print("CPython:", probe())
