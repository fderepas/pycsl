r"""G29 AT2-A8 — a module ATTRIBUTE value (claim != truth; CPython 2)."""
import os
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    return os.SEEK_END


if __name__ == "__main__":
    print("CPython:", probe())
