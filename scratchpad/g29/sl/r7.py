r"""G29 SL-R7 — slice READ clamping probe (claim != truth; CPython 2)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    a = [1, 2, 3]
    b = a[:-1]
    return len(b)


if __name__ == "__main__":
    print("CPython:", probe())
