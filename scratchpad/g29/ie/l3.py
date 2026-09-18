r"""no_exception ValueError over comprehension with int()"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    ss: List[str] = ["x"]
    ys = [int(s) for s in ss]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
