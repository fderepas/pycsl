r"""G29 AL-L7 — route #81's fence lists `append`; `del b[0]` through the alias (claim != truth; CPython 1)."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    a: List[int] = [1, 2]
    b = a
    del b[0]
    return len(a)


if __name__ == "__main__":
    print("CPython:", probe())
