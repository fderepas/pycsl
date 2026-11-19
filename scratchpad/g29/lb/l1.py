r"""stdlib stub: bisect_left contract vs CPython bisect."""
from typing import List
from pycsl_lib.bsect import bisect_left
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    a: List[int] = [1, 3, 5]
    return bisect_left(a, 4, 0, 3)


if __name__ == "__main__":
    import bisect
    print("CPython:", bisect.bisect_left([1, 3, 5], 4, 0, 3))
