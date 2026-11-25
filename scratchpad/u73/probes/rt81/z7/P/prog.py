from zz81z7 import one


#@ ensures \result == 1
def g() -> int:
    return one()


print("result", g())
