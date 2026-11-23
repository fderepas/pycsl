from zpb74.b import one


#@ ensures \result == 1
def g() -> int:
    return one()


print("result", g())
