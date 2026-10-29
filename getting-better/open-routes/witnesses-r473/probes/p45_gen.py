from typing import List, Tuple


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


from typing import Iterator


#@ requires True
#@ ensures True
#@ assigns \nothing
def gen() -> Iterator[List[int]]:
    c: List[int] = []
    yield c


#@ requires True
#@ ensures True
#@ assigns \nothing
def h() -> int:
    for c in gen():
        return g(c)
    return 0


if __name__ == "__main__":
    try:
        print("result", h())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
