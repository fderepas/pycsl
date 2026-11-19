r"""G29 OP-O5 — Optional truthiness vs None-ness (claim != truth; CPython 7)."""
from typing import Optional, List
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    x: Optional[int] = 0
    y = x or 7
    return y


if __name__ == "__main__":
    print("CPython:", probe())
