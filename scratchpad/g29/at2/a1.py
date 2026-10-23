r"""G29 AT2-A1 — a module ATTRIBUTE value (claim != truth; CPython 1)."""
import sys
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return 1 if sys.maxsize > 0 else 0


if __name__ == "__main__":
    print("CPython:", probe())
