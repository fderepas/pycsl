r"""G29 GT8 — same, mutation inline (no call)."""
from typing import List
_ = 0  # anchor
items: List[int] = [0]


#@ ensures \result == True
def probe() -> bool:
    a = items[0]
    items[0] = 9
    b = items[0]
    return a == b


if __name__ == "__main__":
    print("CPython:", probe())
