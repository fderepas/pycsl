r"""f-string repr of string"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s = "a"
    return len(f"{s!r}")


if __name__ == "__main__":
    print("CPython:", probe())
