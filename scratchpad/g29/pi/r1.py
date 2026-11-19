r"""G29 R1 — `__init__` builds a list field by APPENDING to it."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.items: List[int] = []
        self.items.append(k)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(9)
    return len(c.items)


if __name__ == "__main__":
    print("CPython:", probe())
