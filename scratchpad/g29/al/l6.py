r"""G29 AL-L6 — route #81's fence lists `append`; `b += [3]` through the alias (claim != truth; CPython 3)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    a: List[int] = [1, 2]
    b = a
    b += [3]
    return len(a)


if __name__ == "__main__":
    print("CPython:", probe())
