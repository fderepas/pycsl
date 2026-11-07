from typing import List
#@ requires len(xs) == 3
def f(xs: List[int]) -> int:
    i = 0
    #@ loop_invariant len([*xs]) == 1
    #@ loop_invariant 0 <= i and i <= 2
    #@ loop_variant 2 - i
    while i < 2:
        i = i + 1
    return 0


if __name__ == "__main__":
    print(len([*[1, 2, 3]]))
