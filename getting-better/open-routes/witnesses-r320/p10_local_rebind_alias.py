from typing import List
#@ ensures \result == 7
def f() -> int:
    xs = [1, 2]
    ys = xs
    xs = [7, 8]
    return ys[0]

if __name__ == "__main__":
    assert f() == 7, f()
