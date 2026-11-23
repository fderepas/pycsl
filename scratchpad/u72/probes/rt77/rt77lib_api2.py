#@ ensures \result == 1
#@ assigns \nothing
def helper() -> int:
    return 1


#@ ensures \result >= 0
#@ assigns \nothing
def api() -> int:
    return helper()
