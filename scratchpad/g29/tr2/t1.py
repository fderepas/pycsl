r"""trusted function with false ensures used by caller"""
from typing import List, Dict
_ = 0  # anchor


#@ \trusted
#@ ensures \result == 1
def f() -> int:
    return 2


#@ ensures \result == 1
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
