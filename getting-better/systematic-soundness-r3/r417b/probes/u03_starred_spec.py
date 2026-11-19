from typing import List
#@ requires len(xs) == 3
#@ ensures len([*xs]) == 1
def f(xs: List[int]) -> int:
    return 0


if __name__ == "__main__":
    xs = [1, 2, 3]
    f(xs)
    print(len([*xs]))
