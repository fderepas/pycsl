from zz81z8 import one


#@ ensures \result == 1
def g() -> int:
    return one()


print("result", g())
