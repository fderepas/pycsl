#@ ensures \result == 7
#@ assigns \nothing
def abs(x: int) -> int:
    return 7


#@ ensures \result == 7
#@ assigns \nothing
def h(x: int) -> int:
    return abs(x)
