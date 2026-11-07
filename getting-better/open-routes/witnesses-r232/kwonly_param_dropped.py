#@ ensures True
#@ assigns \nothing
def f(*, k: int) -> int:
    return k

#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if f(k=3) == f(k=4):
        return 1
    return 0
