r"""G29 AT2-A2 — a module ATTRIBUTE value (claim != truth; CPython 1)."""
import math
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return 1 if math.pi > 3 else 0


if __name__ == "__main__":
    print("CPython:", probe())
