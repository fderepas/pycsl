from math import *

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if pi % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
