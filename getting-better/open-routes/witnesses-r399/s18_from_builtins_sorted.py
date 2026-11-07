from builtins import sorted
from typing import List


#@ requires len(xs) == 2
#@ ensures \result[0] <= \result[1]
def f(xs: List[int]) -> List[int]:
    return sorted(xs, **{"reverse": True})


if __name__ == "__main__":
    try:
        print("result", f([1, 2]))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
