r"""G29 SL-R6 — slice READ clamping probe (claim != truth; CPython 3)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    s = "hello"
    return len(s[-3:])


if __name__ == "__main__":
    print("CPython:", probe())
