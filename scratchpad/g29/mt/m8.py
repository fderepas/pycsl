r"""match string literal"""
from typing import List, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s = "b"
    match s:
        case "a":
            return 1
        case _:
            return 2


if __name__ == "__main__":
    print("CPython:", probe())
