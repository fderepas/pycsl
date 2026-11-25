#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1

try:
    #@ ensures \result == 2
    #@ assigns \nothing
    def f() -> int:
        return 2
except ImportError:
    pass
