r"""G29 IE-J12 — uncaught list index out of range, no try."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    return xs[5] * 0
if __name__ == "__main__":
    print("CPython:", probe())
