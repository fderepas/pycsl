r"""int parse in loop with handler"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    ss: List[str] = ["1", "x", "2"]
    n = 0
    for s in ss:
        try:
            n = n + int(s)
        except ValueError:
            pass
    return n


if __name__ == "__main__":
    print("CPython:", probe())
