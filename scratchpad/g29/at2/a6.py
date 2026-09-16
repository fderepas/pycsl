r"""G29 AT2-A6 — a module ATTRIBUTE value (claim != truth; CPython 0)."""
import sys
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    return len(sys.argv) - len(sys.argv)


if __name__ == "__main__":
    print("CPython:", probe())
