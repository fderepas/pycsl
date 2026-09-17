r"""G29 SH2 — `from lib import val` FOLLOWED by a local `def val`: Python binds the local def."""
_ = 0  # anchor
from multi_file_lib.shlib import val  # noqa: E402


#@ ensures \result == 100
#@ assigns \nothing
def val() -> int:  # noqa: F811
    return 1


#@ ensures \result == 100
def probe() -> int:
    return val()


if __name__ == "__main__":
    print("CPython:", probe())
