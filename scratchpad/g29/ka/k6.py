r"""default evaluated once shared"""
from typing import List, Dict
_ = 0  # anchor


def f(x: int, acc: Dict[int, int] = {}) -> int:
    acc[x] = x
    return len(acc)


#@ ensures \result == 1
def probe() -> int:
    f(1)
    return f(2)


if __name__ == "__main__":
    print("CPython:", probe())
