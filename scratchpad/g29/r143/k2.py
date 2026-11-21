r"""G29 k2 — route #143 carrier-rerun on gen #29's own refusal: LIM bound inside a module-level if."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f
if True:
    LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
