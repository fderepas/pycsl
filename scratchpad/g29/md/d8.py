r"""G29 MD8 — a class attribute default mutable list shared between instances."""
from typing import List
_ = 0  # anchor


class C:
    items: List[int] = []

    def __init__(self) -> None:
        self.k = 0

    def add(self, v: int) -> None:
        self.items.append(v)


#@ ensures \result == 0
def probe() -> int:
    a = C()
    b = C()
    a.add(1)
    return len(b.items)


if __name__ == "__main__":
    print("CPython:", probe())
