r"""G29 CO-Y8 — an APPEND-built list indexed past its length under no_exception IndexError."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    xs.append(1)
    return xs[3]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
