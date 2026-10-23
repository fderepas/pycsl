r"""G29 K12 — route #143 carrier-rerun on the draft: the callee's module binds LIM only through
its OWN wildcard import, so the dependency-bound-name set misses it."""
_ = 0  # anchor
from multi_file_lib.r143_starlib import f3

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f3(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
