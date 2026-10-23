r"""G29 AT2-A4 — a module ATTRIBUTE value (claim != truth; CPython 1)."""
import os
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return len(os.sep)


if __name__ == "__main__":
    print("CPython:", probe())
