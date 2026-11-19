r"""G29 AT2-A3 — a module ATTRIBUTE value (claim != truth; CPython 10)."""
import string
_ = 0  # anchor


#@ ensures \result != 10
def probe() -> int:
    return len(string.digits)


if __name__ == "__main__":
    print("CPython:", probe())
