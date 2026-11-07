r"""G29 AL-Q3 — appended before the alias, LENGTH read through the alias after a second append through the original is refused? (pop through the original)."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    a: List[int] = []
    a.append(1)
    a.append(2)
    b = a
    a.pop()
    return len(b)


if __name__ == "__main__":
    print("CPython:", probe())
