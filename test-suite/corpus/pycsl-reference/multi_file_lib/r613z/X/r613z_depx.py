# u60 witness 10331 (review rt72 A1, the a1x shape): a library module in an --import-path root (CPython:
# PYTHONPATH). Its absolute import resolves through the PROGRAM's sys.path: the corpus directory first.
from r613z_two import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()
