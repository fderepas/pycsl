from typing import List
#@ requires len(xs) == 1 and len(ys) == 1
#@ ensures ys[0] == \old(ys[0])
#@ assigns xs[0]
def f(xs: List[int], ys: List[int]) -> None:
    xs[0] = ys[0] + 1

if __name__ == "__main__":
    a = [1]; f(a, a); print(a); assert a[0] == 1
