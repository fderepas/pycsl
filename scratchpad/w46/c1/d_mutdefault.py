_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def g(a: list = []) -> int:
    a.append(1)
    return len(a)


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    _x = g()
    return g()
