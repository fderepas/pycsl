r"""G29 OP-O6 — Optional truthiness vs None-ness (claim != truth; CPython 5)."""
from typing import Optional, List
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    x: Optional[int] = 5
    return x if x is not None else -1


if __name__ == "__main__":
    print("CPython:", probe())
