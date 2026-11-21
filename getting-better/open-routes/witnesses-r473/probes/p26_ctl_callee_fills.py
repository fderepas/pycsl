from typing import List


#@ requires len(c) >= 1
#@ ensures True
#@ assigns \nothing
def g(c: List[int]) -> int:
    return c[0]


#@ requires len(c) >= 2
#@ ensures True
#@ assigns \nothing
def g2(c: List[int]) -> int:
    return c[1]


#@ requires True
#@ ensures \result == len(c)
#@ assigns \nothing
def ln(c: List[int]) -> int:
    return len(c)


#@ requires True
#@ ensures True
#@ assigns c
def fill(c: List[int]) -> None:
    c.append(1)


#@ requires True
#@ ensures True
#@ assigns \nothing
def h() -> int:
    c: List[int] = []
    fill(c)
    return g(c)


if __name__ == "__main__":
    try:
        print("result", h())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
