r"""G29 K14 — route #143 in an ENSURES clause: the callee returns ITS module's BASE (-1); the
importer binds BASE = 5 and claims the call returns 5."""
_ = 0  # anchor
from multi_file_lib.r143_enslib import base

BASE = 5


#@ ensures \result == 5
#@ assigns \nothing
def caller() -> int:
    return base()


if __name__ == "__main__":
    print("CPython:", caller())
