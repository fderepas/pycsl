#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return abs(2.5)

if __name__ == "__main__":
    assert f() == 2, f()
