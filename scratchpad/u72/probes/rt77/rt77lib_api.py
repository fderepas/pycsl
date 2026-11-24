#@ ensures \result == 1
#@ assigns \nothing
def helper() -> int:
    return 1


#@ ensures \result == helper()
#@ assigns \nothing
def api() -> int:
    return helper()
