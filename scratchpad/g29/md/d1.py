r"""G29 MD1 — a mutable default list persists across calls."""
from typing import List
_ = 0  # anchor


def add(v: int, acc: List[int] = []) -> int:
    acc.append(v)
    return len(acc)


#@ ensures \result == 1
def probe() -> int:
    add(1)
    return add(2)


if __name__ == "__main__":
    print("CPython:", probe())
