#@ ensures \result == 0
#@ assigns \nothing
def f(*, k: int) -> int:
    return k - k

#@ ensures \result == 7
#@ assigns \nothing
def g(k: int) -> int:
    return k + 7 - k
