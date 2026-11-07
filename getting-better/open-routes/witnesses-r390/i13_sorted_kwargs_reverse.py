from typing import List


#@ requires len(xs) == 2
#@ ensures \result[0] <= \result[1]
def f(xs: List[int]) -> List[int]:
    return sorted(xs, **{"reverse": True})


if __name__ == "__main__":
    r = f([1, 2])
    print("VIOLATION f =", r) if r[0] > r[1] else print("no violation")
