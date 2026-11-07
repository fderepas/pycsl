r"""len of range with step"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    return len(range(0, 10, 3))


if __name__ == "__main__":
    print("CPython:", probe())
