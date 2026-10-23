r"""raise class not instance"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        raise ValueError
    except ValueError:
        return 2
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
