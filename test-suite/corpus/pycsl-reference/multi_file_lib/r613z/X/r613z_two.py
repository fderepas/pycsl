# u60 witness 10331: beside r613z_depx in the --import-path root (sys.path[1]); CPython does not load it.


#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1
