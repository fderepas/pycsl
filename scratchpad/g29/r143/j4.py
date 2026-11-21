r"""G29 J4 — route #143 carrier: the clash is a PARAMETER of the caller named like the callee
module's constant."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f


#@ requires LIM >= 0
#@ assigns \nothing
#@ no_exception ValueError
def caller(LIM: int) -> int:
    return f(LIM)


if __name__ == "__main__":
    print("CPython:", caller(3))
