r"""allow_iteration_mutation append loop result"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    arr: List[int] = [1, 2]
    n = 0
    #@ allow_iteration_mutation
    for x in arr:
        if n < 3:
            arr.append(x)
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
