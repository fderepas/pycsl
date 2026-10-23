r"""G29 SL-R5 — slice READ clamping probe (claim != truth; CPython 4)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    s = "hello"
    return len(s[1:100])


if __name__ == "__main__":
    print("CPython:", probe())
