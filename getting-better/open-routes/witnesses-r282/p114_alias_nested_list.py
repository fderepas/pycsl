from typing import List
#@ requires len(xss) == 2 and len(xss[0]) == 1 and len(xss[1]) == 1
#@ ensures xss[1][0] == \old(xss[1][0])
#@ assigns xss[0][0]
def f(xss: List[List[int]]) -> None:
    xss[0][0] = 9

if __name__ == "__main__":
    r = [0]; m = [r, r]; f(m); print(m); assert m[1][0] == 0
