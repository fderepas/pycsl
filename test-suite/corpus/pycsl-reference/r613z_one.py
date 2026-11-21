# u60 witness 10330 (review rt72 A1): in the program's directory (sys.path[0] of every corpus program),
# so CPython loads THIS file for `from r613z_one import one` inside multi_file_lib/r613z/lib/dep.py.
print("PROGRAM-DIR r613z_one.py loaded:", __file__)


#@ ensures \result == 2
#@ assigns \nothing
def one() -> int:
    return 2
