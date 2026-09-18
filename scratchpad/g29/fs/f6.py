r"""join with separator length"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[str] = ["a", "b", "c"]
    return len(", ".join(xs))


if __name__ == "__main__":
    print("CPython:", probe())
