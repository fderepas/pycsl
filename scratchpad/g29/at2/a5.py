r"""G29 AT2-A5 — a module ATTRIBUTE value (claim != truth; CPython 1)."""
import math
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return int(math.inf > 1)


if __name__ == "__main__":
    print("CPython:", probe())
