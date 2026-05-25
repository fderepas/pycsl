#@ ensures \result == (x * 2)
#@ ensures \result % 2 == 0
#@ assigns \nothing
def double(x: int) -> int:
    return x * 2
