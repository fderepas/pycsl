r"""G29 IE-U2 — starred unpack."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    a, *b = xs
    return len(b)
if __name__ == "__main__":
    print("CPython:", probe())
