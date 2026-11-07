from typing import List
#@ requires len(xs) == 3
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    #@ assert len([*xs]) == 1
    return 0


if __name__ == "__main__":
    print(len([*[1, 2, 3]]))
