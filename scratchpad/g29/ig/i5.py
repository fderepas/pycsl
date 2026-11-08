r"""nested loops break outer only"""
from typing import List, Dict, Iterator
_ = 0  # anchor


#@ ensures \result == 9
def probe() -> int:
    n = 0
    for i in range(3):
        for j in range(3):
            if j == 1:
                break
            n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
