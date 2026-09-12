from typing import List

#@ ensures \result == 2
def f() -> int:
    xs: List[int] = [1, 2, 3]
    xs.pop()
    return len(xs)
if __name__ == "__main__":
    print(f())
