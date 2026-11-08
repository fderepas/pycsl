r"""G29 IE-K2 — no contract; module global state assertion elsewhere depends on handler path."""
from typing import List
_ = 0  # anchor


def m(s: str) -> int:
    try:
        v = int(s)
        return 1
    except ValueError:
        return -1


#@ ensures \result >= 0
def probe() -> int:
    r = m("1.5")
    return r
if __name__ == "__main__":
    print("CPython:", probe())
