#@ ensures \result == 1
def f() -> int:
    x = 0
    return x - (x := 1) + 1

if __name__ == "__main__":
    assert f() == 1
