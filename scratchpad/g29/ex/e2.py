r"""raise from preserves type"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        try:
            raise KeyError()
        except KeyError as k:
            raise ValueError() from k
    except ValueError:
        return 2
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
