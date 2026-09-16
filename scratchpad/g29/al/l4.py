r"""G29 AL-L4 — route #81's fence lists `append`; `b.remove(1)` through the alias (claim != truth; CPython 1)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    a: List[int] = [1, 2]
    b = a
    b.remove(1)
    return len(a)


if __name__ == "__main__":
    print("CPython:", probe())
