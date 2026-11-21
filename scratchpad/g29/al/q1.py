r"""G29 AL-Q1 — route #81's claim "an element STORE through an alias IS faithful", on a list that was APPENDED TO BEFORE the alias (a `ref (seq int)` value)."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a: List[int] = []
    a.append(1)
    b = a
    b[0] = 9
    return a[0]


if __name__ == "__main__":
    print("CPython:", probe())
