import os
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return os.getpid()

if __name__ == "__main__":
    assert f() == 7, f()
