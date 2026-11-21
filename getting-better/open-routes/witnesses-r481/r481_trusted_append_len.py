from typing import List


#@ \trusted
#@ ensures True
def k(xs: List[int]) -> int:
    xs.append(1)
    return 0


#@ ensures \result == \old(len(xs))
def f(xs: List[int]) -> int:
    k(xs)
    return len(xs)


if __name__ == "__main__":
    print("result", f([]), "expected 0")
