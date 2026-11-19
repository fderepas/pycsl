from typing import List

#@ ensures \result == 3
def f() -> int:
    xs: List[int] = [1, 2, 3]
    assert len(xs) == 3
    xs.append(9)
    assert xs[3] == 9
    return len(xs)
if __name__ == "__main__":
    print(f())
