from math import floor
#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return floor(3)

if __name__ == "__main__":
    assert f() == 4, f()
