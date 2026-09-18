r"""type() equality vs isinstance for bool"""
from typing import List, Optional, Union
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    x = True
    return type(x) == int


if __name__ == "__main__":
    print("CPython:", probe())
