r"""G29 OP-O2 — Optional truthiness vs None-ness (claim != truth; CPython 0)."""
from typing import Optional, List
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    x: Optional[str] = ""
    return 1 if x else 0


if __name__ == "__main__":
    print("CPython:", probe())
