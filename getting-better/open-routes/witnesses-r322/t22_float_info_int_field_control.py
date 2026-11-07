import sys
#@ ensures \result >= 0
def f() -> int:
    return sys.float_info.max_10_exp * 0

if __name__ == "__main__":
    assert f() == 0
