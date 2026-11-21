from builtins import sum
#@ ensures \result == 3
def f() -> int:
    return sum([1, 2])
if __name__ == "__main__":
    assert f() == 3
