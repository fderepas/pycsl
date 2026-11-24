from .sub.b import one


#@ ensures \result == 1
def f() -> int:
    return one()
