r"""G29 AL-L5 — route #81's fence lists `append`; `b.clear()` through the alias (claim != truth; CPython 0)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    a: List[int] = [1, 2]
    b = a
    b.clear()
    return len(a)


if __name__ == "__main__":
    print("CPython:", probe())
