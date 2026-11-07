r"""module global rebound at import after def"""
from typing import List, Dict
_ = 0  # anchor


N = 1


def f() -> int:
    return N


N = 2


#@ ensures \result == 1
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
