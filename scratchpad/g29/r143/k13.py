r"""G29 K13 — two-hop wildcard: route #143 carrier-rerun on gen #29's own refusal: LIM reaches the importer through ANOTHER module's wildcard."""
_ = 0  # anchor
from multi_file_lib.r143_hop import *
from multi_file_lib.r141_raiselib import f


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
