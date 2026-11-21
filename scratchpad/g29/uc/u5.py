r"""chr above 127"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    c = chr(233)
    return len(c)


if __name__ == "__main__":
    print("CPython:", probe())
