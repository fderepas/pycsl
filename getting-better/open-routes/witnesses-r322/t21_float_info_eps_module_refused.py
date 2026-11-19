import sys
EPS = sys.float_info.epsilon
#@ ensures \result == 0
def f() -> int:
    return EPS % 1

if __name__ == "__main__":
    assert f() == 0
