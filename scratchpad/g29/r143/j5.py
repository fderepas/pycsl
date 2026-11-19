r"""G29 J5 — route #143 via a MODULE import (`import m as lib; lib.f(k)`)."""
_ = 0  # anchor
import multi_file_lib.r141_raiselib as lib

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return lib.f(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
