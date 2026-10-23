r"""G29 J6 — route #143 via a WILDCARD import, the importer rebinding LIM afterwards."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import *

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
