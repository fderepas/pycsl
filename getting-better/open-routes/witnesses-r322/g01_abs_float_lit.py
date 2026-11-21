#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if abs(2.5) == 2:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
