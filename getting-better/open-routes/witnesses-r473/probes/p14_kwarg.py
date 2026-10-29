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
#@ assigns \nothing
def h() -> int:
    c: List[int] = []
    return g(c=c)


if __name__ == "__main__":
    try:
        print("result", h(*([True] if "b: bool" in """#@ requires True
#@ ensures True
#@ assigns \nothing
def h() -> int:
    c: List[int] = []
    return g(c=c)
""" else ([[7]] if "ys:" in """#@ requires True
#@ ensures True
#@ assigns \nothing
def h() -> int:
    c: List[int] = []
    return g(c=c)
""" else []))))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
