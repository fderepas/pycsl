r"""G29 SC4 — a mutating method called inside a contract."""
from typing import List
_ = 0  # anchor


def pop_len(xs: List[int]) -> int:
    xs.pop()
    return len(xs)


#@ ensures \result == pop_len(xs)
def probe(xs: List[int]) -> int:
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe([1, 2]), pop_len([1, 2]))
