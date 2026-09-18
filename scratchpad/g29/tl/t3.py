r"""handler count increments"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {0: 0}
    errs = 0
    for k in range(3):
        try:
            v = d[k]
        except KeyError:
            errs = errs + 1
    return errs


if __name__ == "__main__":
    print("CPython:", probe())
