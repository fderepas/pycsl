r"""G29 k1 — route #143 carrier-rerun on gen #29's own refusal: LIM reaches the importer from ANOTHER module."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f
from multi_file_lib.r143_other import LIM


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
