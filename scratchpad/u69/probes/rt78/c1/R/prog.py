from hz78c import one


#@ ensures \result == 1
def g() -> int:
    return one()


print("result", g())
