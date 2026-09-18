r"""assert with side effect message"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1]
    assert len(xs) == 1, "ok"
    return len(xs) + 1


if __name__ == "__main__":
    print("CPython:", probe())
