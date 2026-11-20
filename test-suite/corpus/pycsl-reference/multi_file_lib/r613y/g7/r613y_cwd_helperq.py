# u58 witness 10304: the --import-path (CPython: PYTHONPATH) copy, which CPython loads.
print("IMPORT-PATH r613y_cwd_helperq.py loaded:", __file__)


#@ ensures \result == 2
#@ assigns \nothing
def one() -> int:
    return 2
