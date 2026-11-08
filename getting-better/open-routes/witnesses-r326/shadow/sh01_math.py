import math
#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return math.floor(3)

if __name__ == "__main__":
    assert f() == 4, f()
