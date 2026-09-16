r"""G29 AL-Q2 — appended before the alias, element store through the ORIGINAL, read through the alias."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a: List[int] = []
    a.append(1)
    b = a
    a[0] = 9
    return b[0]


if __name__ == "__main__":
    print("CPython:", probe())
