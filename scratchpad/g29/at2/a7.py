r"""G29 AT2-A7 — a module ATTRIBUTE value (claim != truth; CPython 2)."""
import errno
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    return errno.ENOENT


if __name__ == "__main__":
    print("CPython:", probe())
