# u60 witness 10331 (review rt72 A1): in the program's directory (sys.path[0]), so CPython loads THIS
# file for `from r613z_two import one` inside the --import-path module r613z_depx.
print("PROGRAM-DIR r613z_two.py loaded:", __file__)


#@ ensures \result == 2
#@ assigns \nothing
def one() -> int:
    return 2
