r"""abstract function used"""
from typing import List, Dict
_ = 0  # anchor


#@ \abstract
#@ ensures \result >= 0
def f() -> int:
    return -1


#@ ensures \result >= 0
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
