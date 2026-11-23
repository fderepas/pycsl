from zz81z3 import one


#@ ensures \result == 1
def g() -> int:
    return one()


print("result", g())
