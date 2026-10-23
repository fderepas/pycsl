r"""G29 k10 — route #143 carrier-rerun on gen #29's own refusal: the contract CALLS the dependency's helper and the importer defines its own."""
_ = 0  # anchor
from multi_file_lib.r143_fnlib import g


#@ ensures \result == 1
def lim() -> int:
    return 1


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return g(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
