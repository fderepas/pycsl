#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1

if True:
    #@ ensures \result == 2
    #@ assigns \nothing
    def f() -> int:
        return 2
