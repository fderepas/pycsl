r"""except as name deleted after handler"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    e = 1
    try:
        raise ValueError()
    except ValueError as e:
        pass
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
