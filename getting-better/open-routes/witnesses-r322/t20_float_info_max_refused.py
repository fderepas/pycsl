import sys
#@ ensures \result == 0
def f() -> int:
    x = sys.float_info.max
    return x % 1

if __name__ == "__main__":
    assert f() == 0
