r"""iterate string characters"""
from typing import List, Dict, Iterator
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    n = 0
    for ch in "abc":
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
