r"""module global dict built in a loop"""
from typing import List, Dict
_ = 0  # anchor


d: Dict[int, int] = {}
for i in range(3):
    d[i] = i


#@ ensures \result == 0
def probe() -> int:
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
