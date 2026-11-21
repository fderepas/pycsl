# u60 witness 10330 (review rt72 A1): an ABSOLUTE import inside a package module. CPython resolves it
# through the PROGRAM's sys.path (the corpus directory first), not from this directory.
from r613z_one import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()
