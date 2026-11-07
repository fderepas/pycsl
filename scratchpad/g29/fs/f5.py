r"""str.format positional"""
from typing import List
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    return "{1}{0}".format("a", "b") == "ab"


if __name__ == "__main__":
    print("CPython:", probe())
