r"""index error in else caught by outer handler of different try"""
from typing import Dict, List
_ = 0  # anchor


#@ ensures \result == 9
def probe() -> int:
    xs: List[int] = []
    try:
        x = 1
    except IndexError:
        return 9
    else:
        v = xs[0]
    return 9


if __name__ == "__main__":
    print("CPython:", probe())
