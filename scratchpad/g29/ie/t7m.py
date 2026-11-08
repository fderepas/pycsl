r"""no_exception ValueError on a literal tuple unpack arity mismatch through a list"""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    a, b = xs
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
