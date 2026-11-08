import consts19
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if consts19.S * 0 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
