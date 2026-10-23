r"""match value pattern with dotted constant"""
from typing import List, Tuple
_ = 0  # anchor


class K:
    A = 1
    B = 2


#@ ensures \result == 1
def probe() -> int:
    x = 2
    match x:
        case K.A:
            return 1
        case K.B:
            return 2
    return 3


if __name__ == "__main__":
    print("CPython:", probe())
