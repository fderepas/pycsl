r"""G29 NA2 — `a += b` mutates the alias; `a = a + b` does not."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a: List[int] = [1]
    c = a
    a += [2]
    return len(c)


if __name__ == "__main__":
    print("CPython:", probe())
