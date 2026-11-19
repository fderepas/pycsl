#@ ensures \result == 5
def f() -> int:
    x = 0
    y = (x := 5) + x
    return y

if __name__ == "__main__":
    assert f() == 5
