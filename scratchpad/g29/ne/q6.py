r"""G29 NE-Q6 — a subscript on a dict FIELD under no_exception KeyError."""
from typing import Dict
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {1: 2}


#@ no_exception KeyError
def probe() -> int:
    p = P()
    return p.d[5]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
