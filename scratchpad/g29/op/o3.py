r"""G29 OP-O3 — Optional truthiness vs None-ness (claim != truth; CPython 0)."""
from typing import Optional, List
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    x: Optional[int] = None
    x = 0
    return 1 if x is None else 0


if __name__ == "__main__":
    print("CPython:", probe())
