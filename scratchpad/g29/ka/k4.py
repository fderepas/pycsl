r"""kwargs count"""
from typing import List, Dict
_ = 0  # anchor


def f(**kw: int) -> int:
    return len(kw)


#@ ensures \result == 0
def probe() -> int:
    return f(a=1, b=2)


if __name__ == "__main__":
    print("CPython:", probe())
