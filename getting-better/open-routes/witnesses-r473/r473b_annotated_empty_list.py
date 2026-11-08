from typing import List


#@ requires len(c) >= 1
#@ ensures True
#@ assigns \nothing
def g(c: List[int]) -> int:
    return c[0]


#@ requires True
#@ ensures True
#@ assigns \nothing
def h() -> int:
    c: List[int] = []
    return g(c)


if __name__ == "__main__":
    try:
        print("result", h())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
