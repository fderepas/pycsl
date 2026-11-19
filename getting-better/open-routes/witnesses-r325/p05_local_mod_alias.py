import math
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    m = math
    if m.pi % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
