r"""G29 AL-L8 — route #81's fence lists `append`; `b[2:] = [3, 4]` through the alias (claim != truth; CPython 4)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    a: List[int] = [1, 2]
    b = a
    b[2:] = [3, 4]
    return len(a)


if __name__ == "__main__":
    print("CPython:", probe())
