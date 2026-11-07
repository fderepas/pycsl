from typing import List
#@ assigns xs
def g(xs: List[int]) -> None:
    xs.append(3)

#@ ensures \result == 2
def f() -> int:
    a: List[int] = [1, 2]
    g(a)
    return len(a)
if __name__ == "__main__":
    print(f())
