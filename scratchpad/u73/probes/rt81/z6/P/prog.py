from zz81z6 import one


#@ ensures \result == 1
def g() -> int:
    return one()


print("result", g())
