r"""G29 SL-R3 — slice READ clamping probe (claim != truth; CPython 0)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    a = [1, 2, 3]
    b = a[5:]
    return len(b)


if __name__ == "__main__":
    print("CPython:", probe())
